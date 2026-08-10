"""Unit tests — auth passwords, JWT, RBAC."""

from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest

from auth.passwords import hash_password, verify_password
from auth.rbac import assert_permissions, assert_roles, user_has_permission, user_has_role
from auth.tokens import TokenError, create_access_token, create_refresh_token, decode_token
from shared.exceptions.base import ForbiddenError


def test_password_hash_roundtrip():
    hashed = hash_password("S3cretPass!")
    assert hashed != "S3cretPass!"
    assert verify_password("S3cretPass!", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_access_and_refresh():
    secret = "test-secret-key-not-for-prod-32b"
    user_id = uuid.uuid4()
    access = create_access_token(subject=user_id, secret_key=secret, expires_minutes=5)
    payload = decode_token(access, secret_key=secret, expected_type="access")
    assert payload["sub"] == str(user_id)

    refresh = create_refresh_token(subject=user_id, secret_key=secret, jti="abc123")
    refresh_payload = decode_token(refresh, secret_key=secret, expected_type="refresh")
    assert refresh_payload["jti"] == "abc123"


def test_jwt_rejects_wrong_type():
    secret = "test-secret-key-not-for-prod-32b"
    access = create_access_token(subject="u1", secret_key=secret)
    with pytest.raises(TokenError):
        decode_token(access, secret_key=secret, expected_type="refresh")


def _user(*, roles=None, permissions=None, superuser=False):
    role_objs = []
    for name, perms in (roles or {}).items():
        role_objs.append(
            SimpleNamespace(
                name=name,
                permissions=[SimpleNamespace(code=p) for p in perms],
            )
        )
    return SimpleNamespace(
        is_superuser=superuser,
        roles=role_objs,
        role_names=lambda: {r.name for r in role_objs},
        permission_codes=lambda: {p.code for r in role_objs for p in r.permissions},
    )


def test_rbac_role_and_permission():
    user = _user(roles={"member": ["users:read", "api_keys:manage"]})
    assert user_has_role(user, "member")
    assert user_has_permission(user, "users:read")
    assert not user_has_permission(user, "admin:access")
    assert_roles(user, "member")
    with pytest.raises(ForbiddenError):
        assert_permissions(user, "admin:access")


def test_superuser_bypasses_rbac():
    user = _user(superuser=True)
    assert user_has_role(user, "admin")
    assert user_has_permission(user, "anything:goes")
