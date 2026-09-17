"""Authentication use-cases. Framework-agnostic: raises domain errors that the
API layer maps to HTTP responses. Does not commit — the endpoint owns the
transaction."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_expiry,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories import token_repo, user_repo


class AuthError(Exception):
    """Base class for auth failures."""


class EmailAlreadyExists(AuthError):
    pass


class InvalidCredentials(AuthError):
    pass


class InvalidRefreshToken(AuthError):
    pass


@dataclass
class IssuedSession:
    access_token: str
    refresh_token: str  # plaintext, returned to the client via httpOnly cookie
    expires_in: int
    user: User


def _derive_display_name(email: str, display_name: str | None) -> str:
    if display_name:
        return display_name
    return email.split("@", 1)[0][:80]


async def register(
    db: AsyncSession, *, email: str, password: str, display_name: str | None
) -> User:
    email = email.lower()
    if await user_repo.get_by_email(db, email) is not None:
        raise EmailAlreadyExists("An account with this email already exists.")
    user = User(
        email=email,
        password_hash=hash_password(password),
        role=UserRole.PLAYER.value,
        display_name=_derive_display_name(email, display_name),
    )
    user_repo.add(db, user)
    await db.flush()  # populate user.id without committing
    return user


async def authenticate(db: AsyncSession, *, email: str, password: str) -> User:
    user = await user_repo.get_by_email(db, email.lower())
    if user is None or not user.is_active:
        # Still run a hash to keep timing roughly constant against enumeration.
        verify_password(password, "$argon2id$v=19$m=65536,t=3,p=4$" + "A" * 22 + "$" + "A" * 43)
        raise InvalidCredentials("Invalid email or password.")
    if not verify_password(password, user.password_hash):
        raise InvalidCredentials("Invalid email or password.")
    return user


async def issue_session(db: AsyncSession, user: User) -> IssuedSession:
    access = create_access_token(user.id, user.role)
    refresh_plain = generate_refresh_token()
    token_repo.create(
        db,
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_plain),
        expires_at=refresh_expiry(),
    )
    await db.flush()
    return IssuedSession(
        access_token=access,
        refresh_token=refresh_plain,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user,
    )


async def rotate_session(db: AsyncSession, refresh_plain: str | None) -> IssuedSession:
    if not refresh_plain:
        raise InvalidRefreshToken("Missing refresh token.")
    existing = await token_repo.get_active_by_hash(db, hash_refresh_token(refresh_plain))
    if existing is None:
        raise InvalidRefreshToken("Refresh token is invalid, expired, or revoked.")
    user = await user_repo.get_by_id(db, existing.user_id)
    if user is None or not user.is_active:
        raise InvalidRefreshToken("Account is no longer active.")
    token_repo.revoke(existing)  # one-time use: rotate
    return await issue_session(db, user)


async def revoke_session(db: AsyncSession, refresh_plain: str | None) -> None:
    if not refresh_plain:
        return
    existing = await token_repo.get_active_by_hash(db, hash_refresh_token(refresh_plain))
    if existing is not None:
        token_repo.revoke(existing)
