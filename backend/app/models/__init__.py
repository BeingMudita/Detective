"""Import all models so their tables register on Base.metadata
(used by Alembic autogenerate and the test schema builder)."""
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole

__all__ = ["User", "UserRole", "RefreshToken", "AuditLog"]
