"""Authentication endpoints.

The refresh token is delivered as an httpOnly cookie scoped to /auth, so it is
never readable by JavaScript and is only sent to the endpoints that need it.
The short-lived access token is returned in the JSON body (held in memory by
the client).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rate_limit import auth_rate_limit
from app.db.session import get_db
from app.repositories import audit_repo
from app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserPublic
from app.services import auth_service
from app.services.auth_service import (
    EmailAlreadyExists,
    IssuedSession,
    InvalidCredentials,
    InvalidRefreshToken,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.refresh_cookie_path,
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=settings.refresh_cookie_path,
    )


def _token_response(session: IssuedSession, response: Response) -> TokenResponse:
    _set_refresh_cookie(response, session.refresh_token)
    return TokenResponse(
        access_token=session.access_token,
        expires_in=session.expires_in,
        user=UserPublic.model_validate(session.user),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limit)],
)
async def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        user = await auth_service.register(
            db, email=payload.email, password=payload.password, display_name=payload.display_name
        )
    except EmailAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    session = await auth_service.issue_session(db, user)
    audit_repo.record(db, event="auth.register", user_id=user.id, ip=_client_ip(request))
    await db.commit()
    return _token_response(session, response)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(auth_rate_limit)],
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        user = await auth_service.authenticate(db, email=payload.email, password=payload.password)
    except InvalidCredentials as exc:
        audit_repo.record(
            db, event="auth.login_failed", meta={"email": payload.email}, ip=_client_ip(request)
        )
        await db.commit()
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc))
    session = await auth_service.issue_session(db, user)
    audit_repo.record(db, event="auth.login", user_id=user.id, ip=_client_ip(request))
    await db.commit()
    return _token_response(session, response)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(auth_rate_limit)],
)
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    try:
        session = await auth_service.rotate_session(db, cookie)
    except InvalidRefreshToken as exc:
        _clear_refresh_cookie(response)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc))
    audit_repo.record(db, event="auth.refresh", user_id=session.user.id, ip=_client_ip(request))
    await db.commit()
    return _token_response(session, response)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    cookie = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    await auth_service.revoke_session(db, cookie)
    audit_repo.record(db, event="auth.logout", ip=_client_ip(request))
    await db.commit()
    _clear_refresh_cookie(response)
    return MessageResponse(message="Signed out.")
