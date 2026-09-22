"""Static reference data for the client (no auth-sensitive content)."""
from __future__ import annotations

from fastapi import APIRouter

from app.schemas.submission import ATTACK_VECTORS

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/attack-vectors")
async def attack_vectors() -> dict:
    return {"attack_vectors": ATTACK_VECTORS}
