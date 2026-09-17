"""Append-only audit/event writes."""
from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


def record(
    db: AsyncSession,
    *,
    event: str,
    user_id: uuid.UUID | None = None,
    meta: dict | None = None,
    ip: str | None = None,
) -> AuditLog:
    entry = AuditLog(event=event, user_id=user_id, meta=meta, ip=ip)
    db.add(entry)
    return entry
