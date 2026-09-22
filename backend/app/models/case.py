"""Case content model — the authored, data-driven investigation graph.

A case is stored normalized: one ``cases`` row with child rows for entities,
relationships, evidence, OSINT records, timeline events and hints. The same
engine renders any case; adding a case means adding data, not code.

Player-hidden fields (solution rubric, red-herring / solution-actor flags,
relationship correctness) live here but are NEVER serialized to players.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    org: Mapped[str] = mapped_column(String(160), nullable=False, server_default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    learning_objectives: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    # Solution rubric — hidden from players; used by the Phase 4 scoring engine.
    solution: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    content_revision: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now(), nullable=False
    )


class CaseEntity(Base):
    __tablename__ = "case_entities"
    __table_args__ = (UniqueConstraint("case_id", "ext_id", name="uq_case_entity_ext"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ext_id: Mapped[str] = mapped_column(String(64), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    attributes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    is_initial: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_red_herring: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_solution_actor: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")


class Relationship(Base):
    __tablename__ = "relationships"
    __table_args__ = (UniqueConstraint("case_id", "ext_id", name="uq_relationship_ext"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ext_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("case_entities.id", ondelete="CASCADE"), nullable=False
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("case_entities.id", ondelete="CASCADE"), nullable=False
    )
    rel_type: Mapped[str] = mapped_column(String(48), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")
    discoverable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")


class Evidence(Base):
    __tablename__ = "evidence"
    __table_args__ = (UniqueConstraint("case_id", "ext_id", name="uq_evidence_ext"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ext_id: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(48), nullable=False)
    source: Mapped[str] = mapped_column(String(160), nullable=False, server_default="")
    reliability: Mapped[str] = mapped_column(String(16), nullable=False, server_default="medium")
    content: Mapped[str] = mapped_column(Text, nullable=False, server_default="")
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, server_default="")
    relevance_weight: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    related_entity_ext_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    supports_solution: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_red_herring: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_initial: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")


class OsintRecord(Base):
    """A simulated OSINT source response. A lookup that matches (tool, query_key)
    reveals the referenced entities/evidence. This is the pivot mechanic."""

    __tablename__ = "osint_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    tool: Mapped[str] = mapped_column(String(32), nullable=False)
    query_key: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    reveals: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    response: Mapped[str] = mapped_column(Text, nullable=False, server_default="")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"
    __table_args__ = (UniqueConstraint("case_id", "ext_id", name="uq_timeline_ext"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ext_id: Mapped[str] = mapped_column(String(64), nullable=False)
    at: Mapped[str] = mapped_column(String(40), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    actor_ext_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    canonical_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    source: Mapped[str | None] = mapped_column(String(160), nullable=True)
    discoverable: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")


class Hint(Base):
    __tablename__ = "hints"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("cases.id", ondelete="CASCADE"), index=True, nullable=False
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
