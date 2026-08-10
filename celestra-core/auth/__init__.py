"""
Auth module — Celestra Core identity platform.

Provides JWT auth, RBAC, API keys, and FastAPI dependencies for every
Celestra application. Product apps must import this module rather than
implementing their own authentication.
"""

from auth.dependencies import (
    get_auth_service,
    get_current_user,
    get_optional_user,
    require_permissions,
    require_roles,
)
from auth.models import ApiKey, Permission, RefreshToken, Role, User
from auth.schemas import TokenPair, UserCreate, UserLogin, UserRead
from auth.service import AuthService
from auth.router import router as auth_router

__all__ = [
    "ApiKey",
    "AuthService",
    "Permission",
    "RefreshToken",
    "Role",
    "TokenPair",
    "User",
    "UserCreate",
    "UserLogin",
    "UserRead",
    "auth_router",
    "get_auth_service",
    "get_current_user",
    "get_optional_user",
    "require_permissions",
    "require_roles",
]
