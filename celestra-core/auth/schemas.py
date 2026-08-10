"""Auth request/response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
    roles: list[str] = []
    permissions: list[str] = []
    created_at: datetime
    last_login_at: datetime | None = None


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: int | None = Field(default=None, ge=1, le=3650)


class ApiKeyCreated(BaseModel):
    id: UUID
    name: str
    key: str  # plaintext shown once
    key_prefix: str
    scopes: list[str]
    expires_at: datetime | None
    created_at: datetime


class ApiKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    key_prefix: str
    scopes: list[str] = []
    expires_at: datetime | None
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
