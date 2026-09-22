"""investigation engine: cases + investigation runtime

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-17
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── case content ──────────────────────────────────────────────────────────
    op.create_table(
        "cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("difficulty", sa.Integer(), server_default="1", nullable=False),
        sa.Column("org", sa.String(length=160), server_default="", nullable=False),
        sa.Column("summary", sa.Text(), server_default="", nullable=False),
        sa.Column("learning_objectives", sa.JSON(), nullable=False),
        sa.Column("solution", sa.JSON(), nullable=False),
        sa.Column("content_revision", sa.Integer(), server_default="1", nullable=False),
        sa.Column("published", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cases_code", "cases", ["code"], unique=True)

    op.create_table(
        "case_entities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("ext_id", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=False),
        sa.Column("is_initial", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_red_herring", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_solution_actor", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id", "ext_id", name="uq_case_entity_ext"),
    )
    op.create_index("ix_case_entities_case_id", "case_entities", ["case_id"])

    op.create_table(
        "relationships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("ext_id", sa.String(length=64), nullable=False),
        sa.Column("source_entity_id", sa.Uuid(), nullable=False),
        sa.Column("target_entity_id", sa.Uuid(), nullable=False),
        sa.Column("rel_type", sa.String(length=48), nullable=False),
        sa.Column("is_correct", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("discoverable", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_entity_id"], ["case_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["case_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id", "ext_id", name="uq_relationship_ext"),
    )
    op.create_index("ix_relationships_case_id", "relationships", ["case_id"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("ext_id", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=48), nullable=False),
        sa.Column("source", sa.String(length=160), server_default="", nullable=False),
        sa.Column("reliability", sa.String(length=16), server_default="medium", nullable=False),
        sa.Column("content", sa.Text(), server_default="", nullable=False),
        sa.Column("content_hash", sa.String(length=64), server_default="", nullable=False),
        sa.Column("relevance_weight", sa.Integer(), server_default="1", nullable=False),
        sa.Column("related_entity_ext_ids", sa.JSON(), nullable=False),
        sa.Column("supports_solution", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_red_herring", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_initial", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id", "ext_id", name="uq_evidence_ext"),
    )
    op.create_index("ix_evidence_case_id", "evidence", ["case_id"])

    op.create_table(
        "osint_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("tool", sa.String(length=32), nullable=False),
        sa.Column("query_key", sa.String(length=200), nullable=False),
        sa.Column("reveals", sa.JSON(), nullable=False),
        sa.Column("response", sa.Text(), server_default="", nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_osint_records_case_id", "osint_records", ["case_id"])
    op.create_index("ix_osint_records_query_key", "osint_records", ["query_key"])

    op.create_table(
        "timeline_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("ext_id", sa.String(length=64), nullable=False),
        sa.Column("at", sa.String(length=40), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=False),
        sa.Column("actor_ext_id", sa.String(length=64), nullable=True),
        sa.Column("canonical_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("source", sa.String(length=160), nullable=True),
        sa.Column("discoverable", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("case_id", "ext_id", name="uq_timeline_ext"),
    )
    op.create_index("ix_timeline_events_case_id", "timeline_events", ["case_id"])

    op.create_table(
        "hints",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("cost", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_hints_case_id", "hints", ["case_id"])

    # ── investigation runtime ────────────────────────────────────────────────
    op.create_table(
        "investigations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="ACTIVE", nullable=False),
        sa.Column("case_revision", sa.Integer(), server_default="1", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigations_user_id", "investigations", ["user_id"])
    op.create_index("ix_investigations_case_id", "investigations", ["case_id"])

    op.create_table(
        "discovered_entities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("investigation_id", sa.Uuid(), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=False),
        sa.Column("via", sa.String(length=48), server_default="initial", nullable=False),
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entity_id"], ["case_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("investigation_id", "entity_id", name="uq_discovered_entity"),
    )
    op.create_index("ix_discovered_entities_investigation_id", "discovered_entities", ["investigation_id"])

    op.create_table(
        "discovered_evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("investigation_id", sa.Uuid(), nullable=False),
        sa.Column("evidence_id", sa.Uuid(), nullable=False),
        sa.Column("via", sa.String(length=48), server_default="initial", nullable=False),
        sa.Column("collected", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("note", sa.String(length=500), nullable=True),
        sa.Column("tag", sa.String(length=48), nullable=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["evidence_id"], ["evidence.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("investigation_id", "evidence_id", name="uq_discovered_evidence"),
    )
    op.create_index("ix_discovered_evidence_investigation_id", "discovered_evidence", ["investigation_id"])

    op.create_table(
        "player_edges",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("investigation_id", sa.Uuid(), nullable=False),
        sa.Column("source_entity_id", sa.Uuid(), nullable=False),
        sa.Column("target_entity_id", sa.Uuid(), nullable=False),
        sa.Column("rel_type", sa.String(length=48), server_default="linked", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_entity_id"], ["case_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["case_entities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_player_edges_investigation_id", "player_edges", ["investigation_id"])

    op.create_table(
        "investigation_actions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("investigation_id", sa.Uuid(), nullable=False),
        sa.Column("action_type", sa.String(length=48), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["investigation_id"], ["investigations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_investigation_actions_investigation_id", "investigation_actions", ["investigation_id"])
    op.create_index("ix_investigation_actions_action_type", "investigation_actions", ["action_type"])


def downgrade() -> None:
    for table in (
        "investigation_actions",
        "player_edges",
        "discovered_evidence",
        "discovered_entities",
        "investigations",
        "hints",
        "timeline_events",
        "osint_records",
        "evidence",
        "relationships",
        "case_entities",
        "cases",
    ):
        op.drop_table(table)
