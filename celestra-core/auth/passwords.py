"""Password hashing — Argon2id via pwdlib (never store plaintext)."""

from __future__ import annotations

from pwdlib import PasswordHash

_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a stored hash."""
    try:
        return _hasher.verify(password, password_hash)
    except Exception:
        return False
