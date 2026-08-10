"""Platform persistence tables for vectors, billing, analytics, knowledge.

Revision ID: 0003_platform_persistence
Revises: 0002_auth
Create Date: 2026-08-10
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_platform_persistence"
down_revision: Union[str, None] = "0002_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_vector_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("namespace", sa.String(length=128), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_platform_vector_records")),
    )
    op.create_index(op.f("ix_platform_vector_records_namespace"), "platform_vector_records", ["namespace"])

    op.create_table(
        "billing_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", sa.String(length=128), nullable=False),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_billing_subscriptions")),
        sa.UniqueConstraint("account_id", name="uq_billing_subscriptions_account_id"),
    )
    op.create_index(op.f("ix_billing_subscriptions_account_id"), "billing_subscriptions", ["account_id"])

    op.create_table(
        "billing_usage_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("account_id", sa.String(length=128), nullable=False),
        sa.Column("metric", sa.String(length=128), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=32), nullable=False),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_billing_usage_events")),
    )
    op.create_index(op.f("ix_billing_usage_events_account_id"), "billing_usage_events", ["account_id"])
    op.create_index(op.f("ix_billing_usage_events_metric"), "billing_usage_events", ["metric"])

    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("account_id", sa.String(length=128), nullable=True),
        sa.Column("user_id", sa.String(length=128), nullable=True),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_analytics_events")),
    )
    op.create_index(op.f("ix_analytics_events_name"), "analytics_events", ["name"])
    op.create_index(op.f("ix_analytics_events_account_id"), "analytics_events", ["account_id"])
    op.create_index(op.f("ix_analytics_events_user_id"), "analytics_events", ["user_id"])

    op.create_table(
        "knowledge_bases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("document_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_bases")),
        sa.UniqueConstraint("name", name="uq_knowledge_bases_name"),
    )

    op.create_table(
        "knowledge_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=512), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_documents")),
    )
    op.create_index(
        op.f("ix_knowledge_documents_knowledge_base_id"),
        "knowledge_documents",
        ["knowledge_base_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_knowledge_documents_knowledge_base_id"), table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
    op.drop_table("knowledge_bases")
    op.drop_index(op.f("ix_analytics_events_user_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_account_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_name"), table_name="analytics_events")
    op.drop_table("analytics_events")
    op.drop_index(op.f("ix_billing_usage_events_metric"), table_name="billing_usage_events")
    op.drop_index(op.f("ix_billing_usage_events_account_id"), table_name="billing_usage_events")
    op.drop_table("billing_usage_events")
    op.drop_index(op.f("ix_billing_subscriptions_account_id"), table_name="billing_subscriptions")
    op.drop_table("billing_subscriptions")
    op.drop_index(op.f("ix_platform_vector_records_namespace"), table_name="platform_vector_records")
    op.drop_table("platform_vector_records")
