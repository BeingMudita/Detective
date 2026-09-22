"""Read access for case content."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseEntity, Evidence, OsintRecord, Relationship


async def get_by_code(db: AsyncSession, code: str) -> Case | None:
    res = await db.execute(select(Case).where(Case.code == code))
    return res.scalar_one_or_none()


async def get_by_id(db: AsyncSession, case_id: uuid.UUID) -> Case | None:
    res = await db.execute(select(Case).where(Case.id == case_id))
    return res.scalar_one_or_none()


async def list_published(db: AsyncSession) -> list[Case]:
    res = await db.execute(
        select(Case).where(Case.published.is_(True)).order_by(Case.difficulty, Case.code)
    )
    return list(res.scalars().all())


async def entities(db: AsyncSession, case_id: uuid.UUID) -> list[CaseEntity]:
    res = await db.execute(select(CaseEntity).where(CaseEntity.case_id == case_id))
    return list(res.scalars().all())


async def initial_entities(db: AsyncSession, case_id: uuid.UUID) -> list[CaseEntity]:
    res = await db.execute(
        select(CaseEntity).where(
            CaseEntity.case_id == case_id, CaseEntity.is_initial.is_(True)
        )
    )
    return list(res.scalars().all())


async def evidence(db: AsyncSession, case_id: uuid.UUID) -> list[Evidence]:
    res = await db.execute(select(Evidence).where(Evidence.case_id == case_id))
    return list(res.scalars().all())


async def relationships(db: AsyncSession, case_id: uuid.UUID) -> list[Relationship]:
    res = await db.execute(select(Relationship).where(Relationship.case_id == case_id))
    return list(res.scalars().all())


async def match_osint(
    db: AsyncSession, case_id: uuid.UUID, tool: str, query_key: str
) -> OsintRecord | None:
    res = await db.execute(
        select(OsintRecord).where(
            OsintRecord.case_id == case_id,
            OsintRecord.tool == tool,
            OsintRecord.query_key == query_key,
        )
    )
    return res.scalars().first()


async def entities_by_ext(
    db: AsyncSession, case_id: uuid.UUID, ext_ids: list[str]
) -> list[CaseEntity]:
    if not ext_ids:
        return []
    res = await db.execute(
        select(CaseEntity).where(
            CaseEntity.case_id == case_id, CaseEntity.ext_id.in_(ext_ids)
        )
    )
    return list(res.scalars().all())


async def evidence_by_ext(
    db: AsyncSession, case_id: uuid.UUID, ext_ids: list[str]
) -> list[Evidence]:
    if not ext_ids:
        return []
    res = await db.execute(
        select(Evidence).where(Evidence.case_id == case_id, Evidence.ext_id.in_(ext_ids))
    )
    return list(res.scalars().all())
