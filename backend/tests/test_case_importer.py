"""Validation and normalization of authored cases."""
from __future__ import annotations

import copy

import pytest

from app.repositories import case_repo
from app.services.case_importer import CaseImportError, import_case
from tests.conftest import CASE_001


@pytest.mark.asyncio
async def test_valid_case_imports(session_factory):
    async with session_factory() as db:
        case, created = await import_case(db, copy.deepcopy(CASE_001))
        await db.commit()
        assert created is True
        assert case.code == "CASE-001"
        entities = await case_repo.entities(db, case.id)
        evidence = await case_repo.evidence(db, case.id)
        assert len(entities) == 11
        assert len(evidence) == 15
        # the solution actor flag is set from solution.actor
        assert any(e.is_solution_actor for e in entities)
        # red-herring evidence flagged from the solution rubric
        assert any(ev.is_red_herring for ev in evidence)


@pytest.mark.asyncio
async def test_import_is_idempotent(session_factory):
    async with session_factory() as db:
        await import_case(db, copy.deepcopy(CASE_001))
        await db.commit()
    async with session_factory() as db:
        _, created = await import_case(db, copy.deepcopy(CASE_001))
        await db.commit()
        assert created is False


@pytest.mark.asyncio
async def test_unknown_entity_type_rejected(session_factory):
    bad = copy.deepcopy(CASE_001)
    bad["entities"][0]["type"] = "quantum_widget"
    async with session_factory() as db:
        with pytest.raises(CaseImportError):
            await import_case(db, bad)


@pytest.mark.asyncio
async def test_relationship_referencing_unknown_entity_rejected(session_factory):
    bad = copy.deepcopy(CASE_001)
    bad["relationships"].append(
        {"ext_id": "rX", "source": "e_user_nightowl", "target": "e_ghost", "rel_type": "uses"}
    )
    async with session_factory() as db:
        with pytest.raises(CaseImportError):
            await import_case(db, bad)


@pytest.mark.asyncio
async def test_solution_referencing_unknown_actor_rejected(session_factory):
    bad = copy.deepcopy(CASE_001)
    bad["solution"]["actor"] = "e_nobody"
    async with session_factory() as db:
        with pytest.raises(CaseImportError):
            await import_case(db, bad)


@pytest.mark.asyncio
async def test_unreachable_entity_rejected(session_factory):
    bad = copy.deepcopy(CASE_001)
    # An orphan entity that no OSINT record reveals -> unsolvable.
    bad["entities"].append({"ext_id": "e_orphan", "type": "device", "label": "ghost-device"})
    async with session_factory() as db:
        with pytest.raises(CaseImportError):
            await import_case(db, bad)
