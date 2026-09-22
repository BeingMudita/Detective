"""Investigation runtime endpoints. Every route is ownership-checked: a player
can only touch their own investigation (IDOR-proof)."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.investigation import Investigation
from app.models.user import User
from app.repositories import investigation_repo as inv_repo
from app.schemas.investigation import (
    ActionRequest,
    CollectRequest,
    EdgeRequest,
    LookupRequest,
)
from app.schemas.submission import SubmitRequest
from app.services import investigation_service, submission_service
from app.services.investigation_service import InvestigationError

router = APIRouter(prefix="/investigations", tags=["investigations"])


async def get_owned_investigation(
    investigation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Investigation:
    investigation = await inv_repo.get_owned(db, investigation_id, user.id)
    if investigation is None:
        # 404 (not 403) so we don't reveal that someone else's id exists.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Investigation not found")
    return investigation


@router.get("/{investigation_id}")
async def get_state(
    investigation: Investigation = Depends(get_owned_investigation),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await investigation_service.get_state(db, investigation)


@router.post("/{investigation_id}/lookup")
async def lookup(
    payload: LookupRequest,
    investigation: Investigation = Depends(get_owned_investigation),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await investigation_service.lookup(
        db, investigation, payload.tool, payload.query
    )
    await db.commit()
    return result


@router.post("/{investigation_id}/evidence")
async def collect_evidence(
    payload: CollectRequest,
    investigation: Investigation = Depends(get_owned_investigation),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        result = await investigation_service.collect_evidence(
            db, investigation, payload.evidence_ext_id, payload.note, payload.tag
        )
    except InvestigationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    await db.commit()
    return result


@router.post("/{investigation_id}/edges", status_code=status.HTTP_201_CREATED)
async def add_edge(
    payload: EdgeRequest,
    investigation: Investigation = Depends(get_owned_investigation),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        result = await investigation_service.add_edge(
            db, investigation, payload.source, payload.target, payload.rel_type or "linked"
        )
    except InvestigationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    await db.commit()
    return result


@router.post("/{investigation_id}/actions", status_code=status.HTTP_202_ACCEPTED)
async def record_action(
    payload: ActionRequest,
    investigation: Investigation = Depends(get_owned_investigation),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        await investigation_service.record_action(
            db, investigation, payload.action_type, payload.payload
        )
    except InvestigationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    await db.commit()
    return {"ok": True}


@router.post("/{investigation_id}/submit")
async def submit(
    payload: SubmitRequest,
    investigation: Investigation = Depends(get_owned_investigation),
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        debrief = await submission_service.submit(
            db,
            investigation,
            actor_ext_id=payload.actor_ext_id,
            attack_vector=payload.attack_vector,
            cited_evidence=payload.cited_evidence,
            summary=payload.summary,
        )
    except InvestigationError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc))
    await db.commit()
    return debrief
