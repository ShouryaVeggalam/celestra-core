"""Seed default roles and permissions for Celestra Core."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from auth.repository import AuthRepository

DEFAULT_PERMISSIONS: dict[str, str] = {
    "users:read": "Read user profiles",
    "users:write": "Create and update users",
    "api_keys:manage": "Create and revoke API keys",
    "admin:access": "Access administrative surfaces",
    "monitoring:read": "Read metrics and monitoring data",
}

DEFAULT_ROLES: dict[str, list[str]] = {
    "admin": ["users:read", "users:write", "api_keys:manage", "admin:access", "monitoring:read"],
    "member": ["users:read", "api_keys:manage"],
    "viewer": ["users:read", "monitoring:read"],
}


async def seed_rbac(session: AsyncSession) -> None:
    """Idempotently create default roles and permissions."""
    repo = AuthRepository(session)
    permissions = {}
    for code, description in DEFAULT_PERMISSIONS.items():
        permissions[code] = await repo.get_or_create_permission(code, description)

    for role_name, perm_codes in DEFAULT_ROLES.items():
        role = await repo.get_or_create_role(role_name, f"Default {role_name} role")
        existing = {p.code for p in role.permissions}
        for code in perm_codes:
            if code not in existing:
                role.permissions.append(permissions[code])
    await session.flush()
