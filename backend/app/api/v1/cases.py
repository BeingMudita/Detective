"""Case catalog, briefing, and starting an investigation."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories import case_repo
from app.services import investigation_service

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("")
async def list_cases(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[dict]:
    cases = await case_repo.list_published(db)
    catalog = []
    for case in cases:
        initial = await case_repo.initial_entities(db, case.id)
        catalog.append(
            {
                "code": case.code,
                "title": case.title,
                "difficulty": case.difficulty,
                "org": case.org,
                "summary": case.summary,
                "learning_objectives": case.learning_objectives,
                "initial_clues": len(initial),
            }
        )
    return catalog


@router.get("/{code}")
async def get_case_brief(
    code: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    case = await case_repo.get_by_code(db, code)
    if case is None or not case.published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")

    initial_entities = await case_repo.initial_entities(db, case.id)
    all_evidence = await case_repo.evidence(db, case.id)
    return {
        "code": case.code,
        "title": case.title,
        "difficulty": case.difficulty,
        "org": case.org,
        "summary": case.summary,
        "learning_objectives": case.learning_objectives,
        "initial_evidence_package": {
            "entities": [investigation_service.public_entity(e, "initial") for e in initial_entities],
            "evidence": [
                investigation_service.public_evidence(ev, None)
                for ev in all_evidence
                if ev.is_initial
            ],
        },
    }


@router.post("/{code}/start", status_code=status.HTTP_201_CREATED)
async def start_investigation(
    code: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    case = await case_repo.get_by_code(db, code)
    if case is None or not case.published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Case not found")

    investigation, created = await investigation_service.start(db, user.id, case)
    state = await investigation_service.get_state(db, investigation)
    await db.commit()
    return {
        "investigation_id": str(investigation.id),
        "resumed": not created,
        "state": state,
    }
