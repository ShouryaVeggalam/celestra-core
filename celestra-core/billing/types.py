"""Billing domain types — plans, entitlements, usage metering."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid


class PlanTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Plan(BaseModel):
    id: str
    name: str
    description: str = ""
    monthly_price_cents: int = 0
    entitlements: dict[str, int | bool | str] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    account_id: str
    plan_id: str
    status: str = "active"
    created_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class UsageEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(new_uuid()))
    account_id: str
    metric: str  # e.g. ai.tokens, ai.requests, storage.bytes
    quantity: float = 1.0
    unit: str = "count"
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class UsageSummary(BaseModel):
    account_id: str
    metric: str
    total: float
    unit: str = "count"
    event_count: int = 0


class EntitlementCheck(BaseModel):
    account_id: str
    feature: str
    allowed: bool
    limit: int | bool | str | None = None
    usage: float | None = None
    remaining: float | None = None
    plan_id: str | None = None


class RecordUsageRequest(BaseModel):
    account_id: str
    metric: str
    quantity: float = 1.0
    unit: str = "count"
    properties: dict[str, Any] = Field(default_factory=dict)


class AssignPlanRequest(BaseModel):
    account_id: str
    plan_id: str
