"""Normalize a validated case JSON into relational rows.

Validation lives in ``schemas.case_import.CaseIn``; this module only translates
the validated document into ORM rows. Idempotent by case ``code`` (skips by
default; ``replace=True`` rebuilds the case for authoring iteration).
"""
from __future__ import annotations

import hashlib

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import (
    Case,
    CaseEntity,
    Evidence,
    Hint,
    OsintRecord,
    Relationship,
    TimelineEvent,
)
from app.schemas.case_import import CaseIn


class CaseImportError(Exception):
    pass


def normalize_query(value: str) -> str:
    return value.strip().lower()


async def _existing_case(db: AsyncSession, code: str) -> Case | None:
    res = await db.execute(select(Case).where(Case.code == code))
    return res.scalar_one_or_none()


async def _purge_children(db: AsyncSession, case_id) -> None:
    for model in (Relationship, Evidence, OsintRecord, TimelineEvent, Hint, CaseEntity):
        await db.execute(delete(model).where(model.case_id == case_id))


async def import_case(db: AsyncSession, data: dict, *, replace: bool = False) -> tuple[Case, bool]:
    """Import one case. Returns (case, created). Raises CaseImportError on
    invalid content. Does not commit — the caller owns the transaction."""
    try:
        parsed = CaseIn.model_validate(data)
    except Exception as exc:  # pydantic ValidationError or ValueError
        raise CaseImportError(f"Invalid case '{data.get('code', '?')}': {exc}") from exc

    existing = await _existing_case(db, parsed.code)
    if existing is not None and not replace:
        return existing, False

    revision = 1
    if existing is not None:
        revision = existing.content_revision + 1
        await _purge_children(db, existing.id)
        await db.delete(existing)
        await db.flush()

    solution_actor = parsed.solution.actor
    red_herring_evidence = set(parsed.solution.red_herring_evidence)

    case = Case(
        code=parsed.code,
        title=parsed.title,
        difficulty=parsed.difficulty,
        org=parsed.org,
        summary=parsed.summary,
        learning_objectives=parsed.learning_objectives,
        solution=parsed.solution.model_dump(),
        content_revision=revision,
        published=True,
    )
    db.add(case)
    await db.flush()

    # entities
    ext_to_entity: dict[str, CaseEntity] = {}
    for e in parsed.entities:
        entity = CaseEntity(
            case_id=case.id,
            ext_id=e.ext_id,
            type=e.type,
            label=e.label,
            attributes=e.attributes,
            is_initial=e.initial,
            is_red_herring=e.red_herring,
            is_solution_actor=(e.ext_id == solution_actor),
        )
        db.add(entity)
        ext_to_entity[e.ext_id] = entity
    await db.flush()

    # relationships
    for r in parsed.relationships:
        db.add(
            Relationship(
                case_id=case.id,
                ext_id=r.ext_id,
                source_entity_id=ext_to_entity[r.source].id,
                target_entity_id=ext_to_entity[r.target].id,
                rel_type=r.rel_type,
                is_correct=r.correct,
                discoverable=r.discoverable,
            )
        )

    # evidence
    for ev in parsed.evidence:
        db.add(
            Evidence(
                case_id=case.id,
                ext_id=ev.ext_id,
                kind=ev.kind,
                source=ev.source,
                reliability=ev.reliability,
                content=ev.content,
                content_hash=hashlib.sha256(ev.content.encode("utf-8")).hexdigest(),
                relevance_weight=ev.relevance,
                related_entity_ext_ids=ev.related,
                supports_solution=ev.supports_solution,
                is_red_herring=ev.ext_id in red_herring_evidence,
                is_initial=ev.initial,
            )
        )

    # osint records
    for rec in parsed.osint_records:
        db.add(
            OsintRecord(
                case_id=case.id,
                tool=rec.tool,
                query_key=normalize_query(rec.query),
                reveals=rec.reveals.model_dump(),
                response=rec.response,
            )
        )

    # timeline
    for t in parsed.timeline:
        db.add(
            TimelineEvent(
                case_id=case.id,
                ext_id=t.ext_id,
                at=t.at,
                label=t.label,
                actor_ext_id=t.actor,
                canonical_order=t.order,
                source=t.source,
                discoverable=t.discoverable,
            )
        )

    # hints
    for h in parsed.hints:
        db.add(Hint(case_id=case.id, level=h.level, body=h.body, cost=h.cost))

    await db.flush()
    return case, True
