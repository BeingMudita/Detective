"""Investigation runtime: start, fog-of-war state, OSINT lookups (discovery),
evidence collection, and player-drawn relationships.

The server owns the full case graph; players only ever receive their discovered
subset. Player-hidden fields (solution flags, relationship correctness) are
never serialized here.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.case import Case, CaseEntity, Evidence, OsintRecord
from app.models.investigation import (
    DiscoveredEntity,
    DiscoveredEvidence,
    Investigation,
    InvestigationStatus,
    PlayerEdge,
)
from app.repositories import case_repo, investigation_repo as inv_repo
from app.services.case_importer import normalize_query


class InvestigationError(Exception):
    """Player-facing (400-class) investigation error."""


# ── serializers (public, hide solution data) ────────────────────────────────
def public_entity(entity: CaseEntity, via: str | None = None) -> dict:
    return {
        "ext_id": entity.ext_id,
        "type": entity.type,
        "label": entity.label,
        "attributes": entity.attributes or {},
        "via": via,
    }


def public_evidence(ev: Evidence, state: DiscoveredEvidence | None) -> dict:
    return {
        "ext_id": ev.ext_id,
        "kind": ev.kind,
        "source": ev.source,
        "reliability": ev.reliability,
        "content": ev.content,
        "related": ev.related_entity_ext_ids or [],
        "collected": bool(state.collected) if state else False,
        "note": state.note if state else None,
        "tag": state.tag if state else None,
    }


# ── lifecycle ────────────────────────────────────────────────────────────────
async def start(db: AsyncSession, user_id: uuid.UUID, case: Case) -> tuple[Investigation, bool]:
    existing = await inv_repo.get_active_for_case(db, user_id, case.id)
    if existing is not None:
        return existing, False

    investigation = Investigation(
        user_id=user_id,
        case_id=case.id,
        status=InvestigationStatus.ACTIVE.value,
        case_revision=case.content_revision,
    )
    db.add(investigation)
    await db.flush()

    # reveal initial clues
    for entity in await case_repo.initial_entities(db, case.id):
        db.add(
            DiscoveredEntity(
                investigation_id=investigation.id, entity_id=entity.id, via="initial"
            )
        )
    for ev in await case_repo.evidence(db, case.id):
        if ev.is_initial:
            db.add(
                DiscoveredEvidence(
                    investigation_id=investigation.id, evidence_id=ev.id, via="initial"
                )
            )

    inv_repo.log_action(db, investigation.id, "case_started", {"case": case.code})
    await db.flush()
    return investigation, True


async def _osint_tools(db: AsyncSession, case_id: uuid.UUID) -> list[str]:
    res = await db.execute(
        select(distinct(OsintRecord.tool)).where(OsintRecord.case_id == case_id)
    )
    return sorted(res.scalars().all())


async def get_state(db: AsyncSession, investigation: Investigation) -> dict:
    case = await case_repo.get_by_id(db, investigation.case_id)
    assert case is not None

    entities = {e.id: e for e in await case_repo.entities(db, case.id)}
    disc_rows = await inv_repo.discovered_rows(db, investigation.id)
    entities_out = [
        public_entity(entities[d.entity_id], d.via)
        for d in disc_rows
        if d.entity_id in entities
    ]

    evidence = {e.id: e for e in await case_repo.evidence(db, case.id)}
    ev_states = await inv_repo.evidence_rows(db, investigation.id)
    evidence_out = [
        public_evidence(evidence[s.evidence_id], s)
        for s in ev_states
        if s.evidence_id in evidence
    ]

    edges_out = [
        {
            "id": str(edge.id),
            "source": entities[edge.source_entity_id].ext_id,
            "target": entities[edge.target_entity_id].ext_id,
            "rel_type": edge.rel_type,
        }
        for edge in await inv_repo.player_edges(db, investigation.id)
        if edge.source_entity_id in entities and edge.target_entity_id in entities
    ]

    return {
        "investigation": {
            "id": str(investigation.id),
            "status": investigation.status,
            "started_at": investigation.started_at.isoformat(),
        },
        "case": {
            "code": case.code,
            "title": case.title,
            "difficulty": case.difficulty,
            "org": case.org,
            "summary": case.summary,
            "learning_objectives": case.learning_objectives,
        },
        "tools": await _osint_tools(db, case.id),
        "entities": entities_out,
        "evidence": evidence_out,
        "edges": edges_out,
        "counts": {
            "entities_discovered": len(entities_out),
            "evidence_discovered": len(evidence_out),
            "evidence_collected": sum(1 for s in ev_states if s.collected),
            "relationships_drawn": len(edges_out),
        },
    }


# ── discovery (the OSINT lookup) ─────────────────────────────────────────────
async def lookup(db: AsyncSession, investigation: Investigation, tool: str, query: str) -> dict:
    case_id = investigation.case_id
    q = normalize_query(query)

    entities = {e.id: e for e in await case_repo.entities(db, case_id)}
    discovered_ids = await inv_repo.discovered_entity_ids(db, investigation.id)
    discovered_labels = {
        entities[eid].label.strip().lower() for eid in discovered_ids if eid in entities
    }

    record = await case_repo.match_osint(db, case_id, tool, q)
    # Anti-brute-force: you can only investigate a lead you've already surfaced.
    unlocked = q in discovered_labels

    if record is None or not unlocked:
        inv_repo.log_action(
            db, investigation.id, "search_performed", {"tool": tool, "query": query, "hit": False}
        )
        await db.flush()
        return {
            "tool": tool,
            "query": query,
            "hit": False,
            "message": "No new leads surfaced from that lookup.",
            "revealed": {"entities": [], "evidence": []},
        }

    reveals = record.reveals or {}
    # reveal entities
    new_entities: list[dict] = []
    for entity in await case_repo.entities_by_ext(db, case_id, reveals.get("entities", [])):
        if entity.id not in discovered_ids:
            db.add(
                DiscoveredEntity(
                    investigation_id=investigation.id,
                    entity_id=entity.id,
                    via=f"lookup:{tool}",
                )
            )
            discovered_ids.add(entity.id)
            new_entities.append(public_entity(entity, f"lookup:{tool}"))

    # reveal evidence
    already_ev = await inv_repo.discovered_evidence_ids(db, investigation.id)
    new_evidence: list[dict] = []
    for ev in await case_repo.evidence_by_ext(db, case_id, reveals.get("evidence", [])):
        if ev.id not in already_ev:
            db.add(
                DiscoveredEvidence(
                    investigation_id=investigation.id,
                    evidence_id=ev.id,
                    via=f"lookup:{tool}",
                )
            )
            already_ev.add(ev.id)
            new_evidence.append(public_evidence(ev, None))

    inv_repo.log_action(
        db,
        investigation.id,
        "search_performed",
        {
            "tool": tool,
            "query": query,
            "hit": True,
            "revealed_entities": [e["ext_id"] for e in new_entities],
            "revealed_evidence": [e["ext_id"] for e in new_evidence],
        },
    )
    await db.flush()
    return {
        "tool": tool,
        "query": query,
        "hit": True,
        "message": record.response or "New leads surfaced.",
        "revealed": {"entities": new_entities, "evidence": new_evidence},
    }


# ── evidence collection ──────────────────────────────────────────────────────
async def collect_evidence(
    db: AsyncSession,
    investigation: Investigation,
    evidence_ext_id: str,
    note: str | None,
    tag: str | None,
) -> dict:
    ev_list = await case_repo.evidence_by_ext(db, investigation.case_id, [evidence_ext_id])
    if not ev_list:
        raise InvestigationError("No such evidence in this case.")
    ev = ev_list[0]
    state = await inv_repo.get_evidence_state(db, investigation.id, ev.id)
    if state is None:
        raise InvestigationError("You haven't discovered that evidence yet.")

    state.collected = True
    state.note = note
    state.tag = tag
    state.collected_at = datetime.now(timezone.utc)
    inv_repo.log_action(
        db,
        investigation.id,
        "evidence_collected",
        {"evidence": evidence_ext_id, "tag": tag},
    )
    await db.flush()
    return public_evidence(ev, state)


# ── player-drawn relationships ───────────────────────────────────────────────
async def add_edge(
    db: AsyncSession,
    investigation: Investigation,
    source_ext: str,
    target_ext: str,
    rel_type: str,
) -> dict:
    if source_ext == target_ext:
        raise InvestigationError("An entity cannot be linked to itself.")
    found = {
        e.ext_id: e
        for e in await case_repo.entities_by_ext(
            db, investigation.case_id, [source_ext, target_ext]
        )
    }
    if source_ext not in found or target_ext not in found:
        raise InvestigationError("Both endpoints must be entities in this case.")

    discovered = await inv_repo.discovered_entity_ids(db, investigation.id)
    if found[source_ext].id not in discovered or found[target_ext].id not in discovered:
        raise InvestigationError("You can only connect entities you have discovered.")

    edge = PlayerEdge(
        investigation_id=investigation.id,
        source_entity_id=found[source_ext].id,
        target_entity_id=found[target_ext].id,
        rel_type=rel_type or "linked",
    )
    db.add(edge)
    inv_repo.log_action(
        db,
        investigation.id,
        "relationship_created",
        {"source": source_ext, "target": target_ext, "rel_type": rel_type},
    )
    await db.flush()
    return {
        "id": str(edge.id),
        "source": source_ext,
        "target": target_ext,
        "rel_type": edge.rel_type,
    }


# ── generic action logging ───────────────────────────────────────────────────
ALLOWED_ACTIONS = {"entity_viewed", "note_created", "evidence_pinned", "tool_opened"}


async def record_action(
    db: AsyncSession, investigation: Investigation, action_type: str, payload: dict
) -> None:
    if action_type not in ALLOWED_ACTIONS:
        raise InvestigationError(f"Unsupported action '{action_type}'.")
    inv_repo.log_action(db, investigation.id, action_type, payload or {})
    await db.flush()
