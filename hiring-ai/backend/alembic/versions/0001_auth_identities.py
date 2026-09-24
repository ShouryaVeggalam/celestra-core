"""auth identities + core auth tables

Revision ID: 0001_auth_identities
Revises:
Create Date: 2026-09-24
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_auth_identities"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_table(
        "auth_identities",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("provider", "subject", name="uq_auth_identities_provider_subject"),
    )
    op.create_index("ix_auth_identities_provider", "auth_identities", ["provider"])
    op.create_index("ix_auth_identities_subject", "auth_identities", ["subject"])
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"])
    op.create_table(
        "memberships",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("org_id", "user_id", name="uq_memberships_org_user"),
    )
    op.create_table(
        "invite_codes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("used_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("code_hash", name="uq_invite_codes_code_hash"),
    )
    op.create_index("ix_invite_codes_org_id", "invite_codes", ["org_id"])
    op.create_table(
        "hiring_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("org_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_hiring_events_org_id", "hiring_events", ["org_id"])


def downgrade() -> None:
    op.drop_table("hiring_events")
    op.drop_table("invite_codes")
    op.drop_table("memberships")
    op.drop_table("auth_identities")
    op.drop_table("organizations")
    op.drop_table("users")
