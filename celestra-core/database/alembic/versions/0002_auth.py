"""Auth identity, RBAC, API keys, refresh tokens.

Revision ID: 0002_auth
Revises: 0001_foundation
Create Date: 2026-08-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_auth"
down_revision: Union[str, None] = "0001_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "auth_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_users")),
        sa.UniqueConstraint("email", name=op.f("uq_auth_users_email")),
    )
    op.create_index(op.f("ix_auth_users_email"), "auth_users", ["email"], unique=False)

    op.create_table(
        "auth_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_roles")),
        sa.UniqueConstraint("name", name="uq_auth_roles_name"),
    )

    op.create_table(
        "auth_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_permissions")),
        sa.UniqueConstraint("code", name="uq_auth_permissions_code"),
    )

    op.create_table(
        "auth_user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["auth_roles.id"], name=op.f("fk_auth_user_roles_role_id_auth_roles"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], name=op.f("fk_auth_user_roles_user_id_auth_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "auth_role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["auth_permissions.id"],
            name=op.f("fk_auth_role_permissions_permission_id_auth_permissions"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["auth_roles.id"],
            name=op.f("fk_auth_role_permissions_role_id_auth_roles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "auth_api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("key_prefix", sa.String(length=16), nullable=False),
        sa.Column("key_hash", sa.String(length=255), nullable=False),
        sa.Column("scopes", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], name=op.f("fk_auth_api_keys_user_id_auth_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_api_keys")),
    )
    op.create_index(op.f("ix_auth_api_keys_key_prefix"), "auth_api_keys", ["key_prefix"], unique=False)
    op.create_index(op.f("ix_auth_api_keys_user_id"), "auth_api_keys", ["user_id"], unique=False)

    op.create_table(
        "auth_refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["auth_users.id"],
            name=op.f("fk_auth_refresh_tokens_user_id_auth_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_auth_refresh_tokens")),
        sa.UniqueConstraint("jti", name=op.f("uq_auth_refresh_tokens_jti")),
    )
    op.create_index(op.f("ix_auth_refresh_tokens_jti"), "auth_refresh_tokens", ["jti"], unique=False)
    op.create_index(op.f("ix_auth_refresh_tokens_user_id"), "auth_refresh_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_refresh_tokens_user_id"), table_name="auth_refresh_tokens")
    op.drop_index(op.f("ix_auth_refresh_tokens_jti"), table_name="auth_refresh_tokens")
    op.drop_table("auth_refresh_tokens")
    op.drop_index(op.f("ix_auth_api_keys_user_id"), table_name="auth_api_keys")
    op.drop_index(op.f("ix_auth_api_keys_key_prefix"), table_name="auth_api_keys")
    op.drop_table("auth_api_keys")
    op.drop_table("auth_role_permissions")
    op.drop_table("auth_user_roles")
    op.drop_table("auth_permissions")
    op.drop_table("auth_roles")
    op.drop_index(op.f("ix_auth_users_email"), table_name="auth_users")
    op.drop_table("auth_users")
