"""Load authored case JSON files from backend/cases/ into the database.

Idempotent: existing cases (by code) are skipped. Run via
`python -m app.import_cases` (the Docker entrypoint does this automatically).
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.services.case_importer import CaseImportError, import_case

logger = get_logger("import_cases")

CASES_DIR = Path(__file__).resolve().parents[1] / "cases"


async def run() -> None:
    files = sorted(CASES_DIR.glob("*.json"))
    if not files:
        logger.warning("No case files found in %s", CASES_DIR)
        return
    async with AsyncSessionLocal() as db:
        for path in files:
            data = json.loads(path.read_text(encoding="utf-8"))
            try:
                case, created = await import_case(db, data)
            except CaseImportError as exc:
                logger.error("Import failed for %s: %s", path.name, exc)
                raise
            logger.info("%s: %s", "imported" if created else "already present", case.code)
        await db.commit()
    logger.info("Case import complete (%d file(s)).", len(files))


if __name__ == "__main__":
    asyncio.run(run())
