"""
Billing module — metering, plans, and entitlements for Celestra apps.

Product apps must not invent their own usage ledgers; import BillingService.
"""

from __future__ import annotations

from typing import Any

from billing.service import BillingService
from billing.types import (
    AssignPlanRequest,
    EntitlementCheck,
    Plan,
    RecordUsageRequest,
    Subscription,
    UsageEvent,
)

__all__ = [
    "AssignPlanRequest",
    "BillingService",
    "EntitlementCheck",
    "Plan",
    "RecordUsageRequest",
    "Subscription",
    "UsageEvent",
    "billing_router",
]


def __getattr__(name: str) -> Any:
    if name == "billing_router":
        from billing.http import router as billing_router

        return billing_router
    raise AttributeError(name)
