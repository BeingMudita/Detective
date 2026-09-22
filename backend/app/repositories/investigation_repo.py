"""Read/write access for per-player investigation state."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investigation import (
    DiscoveredEntity,
    DiscoveredEvidence,
    Investigation,
    InvestigationAction,
    InvestigationStatus,
    PlayerEdge,
)


async def get_owned(
    db: AsyncSession, investigation_id: uuid.UUID, user_id: uuid.UUID
) -> Investigation | None:
    res = await db.execute(
        select(Investigation).where(
            Investigation.id == investigation_id, Investigation.user_id == user_id
        )
    )
    return res.scalar_one_or_none()


async def get_active_for_case(
    db: AsyncSession, user_id: uuid.UUID, case_id: uuid.UUID
) -> Investigation | None:
    res = await db.execute(
        select(Investigation).where(
            Investigation.user_id == user_id,
            Investigation.case_id == case_id,
            Investigation.status == InvestigationStatus.ACTIVE.value,
        )
    )
    return res.scalars().first()


async def discovered_entity_ids(
    db: AsyncSession, investigation_id: uuid.UUID
) -> set[uuid.UUID]:
    res = await db.execute(
        select(DiscoveredEntity.entity_id).where(
            DiscoveredEntity.investigation_id == investigation_id
        )
    )
    return set(res.scalars().all())


async def discovered_rows(
    db: AsyncSession, investigation_id: uuid.UUID
) -> list[DiscoveredEntity]:
    res = await db.execute(
        select(DiscoveredEntity).where(
            DiscoveredEntity.investigation_id == investigation_id
        )
    )
    return list(res.scalars().all())


async def evidence_rows(
    db: AsyncSession, investigation_id: uuid.UUID
) -> list[DiscoveredEvidence]:
    res = await db.execute(
        select(DiscoveredEvidence).where(
            DiscoveredEvidence.investigation_id == investigation_id
        )
    )
    return list(res.scalars().all())


async def get_evidence_state(
    db: AsyncSession, investigation_id: uuid.UUID, evidence_id: uuid.UUID
) -> DiscoveredEvidence | None:
    res = await db.execute(
        select(DiscoveredEvidence).where(
            DiscoveredEvidence.investigation_id == investigation_id,
            DiscoveredEvidence.evidence_id == evidence_id,
        )
    )
    return res.scalar_one_or_none()


async def discovered_evidence_ids(
    db: AsyncSession, investigation_id: uuid.UUID
) -> set[uuid.UUID]:
    res = await db.execute(
        select(DiscoveredEvidence.evidence_id).where(
            DiscoveredEvidence.investigation_id == investigation_id
        )
    )
    return set(res.scalars().all())


async def player_edges(db: AsyncSession, investigation_id: uuid.UUID) -> list[PlayerEdge]:
    res = await db.execute(
        select(PlayerEdge).where(PlayerEdge.investigation_id == investigation_id)
    )
    return list(res.scalars().all())


def log_action(
    db: AsyncSession, investigation_id: uuid.UUID, action_type: str, payload: dict | None = None
) -> InvestigationAction:
    action = InvestigationAction(
        investigation_id=investigation_id, action_type=action_type, payload=payload or {}
    )
    db.add(action)
    return action
