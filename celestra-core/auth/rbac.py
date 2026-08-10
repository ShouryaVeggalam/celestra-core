"""RBAC helpers — roles and permissions checks."""

from __future__ import annotations

from auth.models import User
from shared.exceptions.base import ForbiddenError


def user_has_role(user: User, *roles: str) -> bool:
    if user.is_superuser:
        return True
    names = user.role_names()
    return any(role in names for role in roles)


def user_has_permission(user: User, *permissions: str) -> bool:
    if user.is_superuser:
        return True
    codes = user.permission_codes()
    return any(code in codes for code in permissions)


def user_has_all_permissions(user: User, *permissions: str) -> bool:
    if user.is_superuser:
        return True
    codes = user.permission_codes()
    return all(code in codes for code in permissions)


def assert_roles(user: User, *roles: str) -> None:
    if not user_has_role(user, *roles):
        raise ForbiddenError(
            "Insufficient role",
            details={"required_roles": list(roles)},
        )


def assert_permissions(user: User, *permissions: str, require_all: bool = False) -> None:
    ok = (
        user_has_all_permissions(user, *permissions)
        if require_all
        else user_has_permission(user, *permissions)
    )
    if not ok:
        raise ForbiddenError(
            "Insufficient permissions",
            details={"required_permissions": list(permissions)},
        )
