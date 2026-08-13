"""External identity mapping for Revenue ↔ Core bridge.

Revision ID: 0004_auth_bridge
Revises: 0003_platform_persistence
Create Date: 2026-08-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_auth_bridge"
down_revision: Union[str, None] = "0003_platform_persistence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_external_identities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("application", sa.String(length=64), nullable=False),
        sa.Column("external_subject", sa.String(length=255), nullable=False),
        sa.Column("external_user_id", sa.String(length=128), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth_users.id"],
            name=op.f("fk_auth_external_identities_user_id_auth_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_external_identities")),
        sa.UniqueConstraint(
            "provider",
            "application",
            "external_subject",
            name="uq_auth_external_identities_subject",
        ),
        sa.UniqueConstraint("user_id", name="uq_auth_external_identities_user_id"),
    )
    op.create_index(
        op.f("ix_auth_external_identities_provider"),
        "auth_external_identities",
        ["provider"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_external_identities_application"),
        "auth_external_identities",
        ["application"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_external_identities_external_subject"),
        "auth_external_identities",
        ["external_subject"],
        unique=False,
    )
    op.create_index(
        op.f("ix_auth_external_identities_user_id"),
        "auth_external_identities",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_external_identities_user_id"), table_name="auth_external_identities")
    op.drop_index(
        op.f("ix_auth_external_identities_external_subject"),
        table_name="auth_external_identities",
    )
    op.drop_index(
        op.f("ix_auth_external_identities_application"),
        table_name="auth_external_identities",
    )
    op.drop_index(
        op.f("ix_auth_external_identities_provider"),
        table_name="auth_external_identities",
    )
    op.drop_table("auth_external_identities")
