"""Guard: every authored case in backend/cases/ must import cleanly.

This runs the full validator (referential integrity + solvability/reachability)
over each case JSON, so a broken new case fails CI rather than at play time.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.repositories import case_repo
from app.services.case_importer import import_case

CASES_DIR = Path(__file__).resolve().parents[1] / "cases"
CASE_FILES = sorted(CASES_DIR.glob("*.json"))


def test_cases_directory_is_not_empty():
    assert CASE_FILES, "no case files found in backend/cases/"


@pytest.mark.parametrize("path", CASE_FILES, ids=lambda p: p.name)
@pytest.mark.asyncio
async def test_case_file_imports(path: Path, session_factory):
    data = json.loads(path.read_text(encoding="utf-8"))
    async with session_factory() as db:
        case, created = await import_case(db, data)
        await db.commit()
        assert created is True
        assert case.code == data["code"]
        # every case is solvable end-to-end: at least the actor must exist
        entities = {e.ext_id for e in await case_repo.entities(db, case.id)}
        assert data["solution"]["actor"] in entities
