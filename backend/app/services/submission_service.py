"""Final case submission + a lightweight debrief.

Phase 3 records the conclusion and reveals the solution afterwards with a basic
correctness read-out. The full deterministic 6-dimension score is Phase 4.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.investigation import Investigation, InvestigationStatus
from app.models.submission import Submission
from app.repositories import case_repo, investigation_repo as inv_repo
from app.schemas.submission import ATTACK_VECTORS
from app.services.investigation_service import InvestigationError


async def submit(
    db: AsyncSession,
    investigation: Investigation,
    *,
    actor_ext_id: str,
    attack_vector: str,
    cited_evidence: list[str],
    summary: str,
) -> dict:
    if investigation.status != InvestigationStatus.ACTIVE.value:
        raise InvestigationError("This investigation has already been submitted.")
    if attack_vector not in ATTACK_VECTORS:
        raise InvestigationError("Unknown attack vector.")

    case = await case_repo.get_by_id(db, investigation.case_id)
    assert case is not None

    entities = {e.ext_id: e for e in await case_repo.entities(db, case.id)}
    if actor_ext_id not in entities:
        raise InvestigationError("The named actor is not an entity in this case.")

    discovered_ids = await inv_repo.discovered_entity_ids(db, investigation.id)
    if entities[actor_ext_id].id not in discovered_ids:
        raise InvestigationError("You can only accuse an entity you have discovered.")

    # collected evidence ext ids
    evidence = {e.id: e for e in await case_repo.evidence(db, case.id)}
    collected = {
        evidence[s.evidence_id].ext_id
        for s in await inv_repo.evidence_rows(db, investigation.id)
        if s.collected and s.evidence_id in evidence
    }

    solution = case.solution or {}
    required = set(solution.get("required_evidence", []))
    red_herrings = set(solution.get("red_herring_evidence", []))

    result = {
        "correct_actor": actor_ext_id == solution.get("actor"),
        "correct_vector": attack_vector == solution.get("attack_vector"),
        "required_collected": sorted(required & collected),
        "required_total": len(required),
        "red_herrings_collected": sorted(red_herrings & collected),
        "entities_discovered": len(discovered_ids),
        "evidence_collected": len(collected),
    }

    answers = {
        "actor_ext_id": actor_ext_id,
        "attack_vector": attack_vector,
        "cited_evidence": cited_evidence,
        "summary": summary,
    }

    db.add(
        Submission(investigation_id=investigation.id, answers=answers, result=result)
    )
    investigation.status = InvestigationStatus.SUBMITTED.value
    investigation.submitted_at = datetime.now(timezone.utc)
    inv_repo.log_action(db, investigation.id, "case_submitted", {"actor": actor_ext_id})
    await db.flush()

    return {
        "verdict": result,
        "solution": {
            "actor_ext_id": solution.get("actor"),
            "actor_label": entities[solution["actor"]].label if solution.get("actor") in entities else None,
            "attack_vector": solution.get("attack_vector"),
            "required_evidence": sorted(required),
            "red_herring_evidence": sorted(red_herrings),
        },
        "message": (
            "Strong work — the evidence backs your conclusion."
            if result["correct_actor"] and result["correct_vector"]
            else "Case closed. Review the debrief to see where the evidence pointed."
        ),
        "note": "A full scored evaluation across six reasoning dimensions arrives in the next release.",
    }
