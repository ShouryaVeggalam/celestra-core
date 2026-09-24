"""Invite code hashing helpers."""

from __future__ import annotations

import hashlib
import secrets
import string


ALPHABET = string.ascii_uppercase + string.digits


def generate_invite_code(length: int = 8) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def normalize_invite_code(code: str) -> str:
    return "".join(ch for ch in code.strip().upper() if ch.isalnum())


def hash_invite_code(code: str, *, pepper: str) -> str:
    normalized = normalize_invite_code(code)
    material = f"{pepper}:{normalized}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()
