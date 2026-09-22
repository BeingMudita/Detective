"""Per-player investigation runtime state (the fog of war over a case graph)."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class InvestigationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUBMITTED = "SUBMITTED"
    ABANDONED = "ABANDONED"


class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="ACTIVE")
    case_revision: Mapped[int] = mapped_column(nullable=False, server_default="1")
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DiscoveredEntity(Base):
    __tablename__ = "discovered_entities"
    __table_args__ = (
        UniqueConstraint("investigation_id", "entity_id", name="uq_discovered_entity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("case_entities.id", ondelete="CASCADE"), nullable=False
    )
    via: Mapped[str] = mapped_column(String(48), nullable=False, server_default="initial")
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )


class DiscoveredEvidence(Base):
    """Evidence the player has encountered. ``collected`` marks whether they
    filed it into the case (a deliberate, scored action); note/tag are the
    player's annotations."""

    __tablename__ = "discovered_evidence"
    __table_args__ = (
        UniqueConstraint("investigation_id", "evidence_id", name="uq_discovered_evidence"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    evidence_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False
    )
    via: Mapped[str] = mapped_column(String(48), nullable=False, server_default="initial")
    collected: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tag: Mapped[str | None] = mapped_column(String(48), nullable=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PlayerEdge(Base):
    """A relationship the player asserts between two discovered entities."""

    __tablename__ = "player_edges"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("case_entities.id", ondelete="CASCADE"), nullable=False
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("case_entities.id", ondelete="CASCADE"), nullable=False
    )
    rel_type: Mapped[str] = mapped_column(String(48), nullable=False, server_default="linked")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )


class InvestigationAction(Base):
    """Append-only per-investigation event stream — the substrate for scoring,
    analytics, anti-cheat and research."""

    __tablename__ = "investigation_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    investigation_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("investigations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(48), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )
