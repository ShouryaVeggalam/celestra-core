"""Password hashing — Argon2id via pwdlib (never store plaintext)."""

from __future__ import annotations

import secrets

from pwdlib import PasswordHash

_hasher = PasswordHash.recommended()

# Bridge-provisioned users cannot log in via password. Stored value is never a
# valid Argon2 hash; login rejects this prefix before verify.
UNUSABLE_PASSWORD_PREFIX = "!celestra.unusable$"


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return _hasher.hash(password)


def make_unusable_password() -> str:
    """Return a stored password marker that can never verify."""
    return f"{UNUSABLE_PASSWORD_PREFIX}{secrets.token_hex(32)}"


def is_unusable_password(password_hash: str) -> bool:
    return (password_hash or "").startswith(UNUSABLE_PASSWORD_PREFIX)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a stored hash."""
    if is_unusable_password(password_hash):
        return False
    try:
        return _hasher.verify(password, password_hash)
    except Exception:
        return False