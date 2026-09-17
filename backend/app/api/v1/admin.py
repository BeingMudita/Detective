"""Admin-only endpoints. In Phase 1 this exists to prove RBAC end-to-end;
Phase 6 fills it with case-management CRUD."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
async def admin_ping(admin: User = Depends(require_role(UserRole.ADMIN))) -> dict:
    return {"ok": True, "admin": admin.email, "message": "Admin access confirmed."}
