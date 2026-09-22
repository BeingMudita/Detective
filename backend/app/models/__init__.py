"""Import all models so their tables register on Base.metadata
(used by Alembic autogenerate and the test schema builder)."""
from app.models.audit_log import AuditLog
from app.models.case import (
    Case,
    CaseEntity,
    Evidence,
    Hint,
    OsintRecord,
    Relationship,
    TimelineEvent,
)
from app.models.investigation import (
    DiscoveredEntity,
    DiscoveredEvidence,
    Investigation,
    InvestigationAction,
    InvestigationStatus,
    PlayerEdge,
)
from app.models.refresh_token import RefreshToken
from app.models.submission import Submission
from app.models.user import User, UserRole

__all__ = [
    "User",
    "UserRole",
    "RefreshToken",
    "AuditLog",
    "Case",
    "CaseEntity",
    "Relationship",
    "Evidence",
    "OsintRecord",
    "TimelineEvent",
    "Hint",
    "Investigation",
    "InvestigationStatus",
    "DiscoveredEntity",
    "DiscoveredEvidence",
    "PlayerEdge",
    "InvestigationAction",
    "Submission",
]
