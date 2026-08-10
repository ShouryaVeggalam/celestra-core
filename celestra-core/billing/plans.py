"""Default Celestra commercial plans."""

from __future__ import annotations

from billing.types import Plan

DEFAULT_PLANS: dict[str, Plan] = {
    "free": Plan(
        id="free",
        name="Free",
        description="Development and evaluation",
        monthly_price_cents=0,
        entitlements={
            "ai.requests_per_day": 100,
            "ai.tokens_per_day": 50_000,
            "storage.bytes": 100_000_000,
            "agents.enabled": True,
            "knowledge.bases": 1,
            "workflows.enabled": True,
        },
    ),
    "pro": Plan(
        id="pro",
        name="Pro",
        description="Production apps",
        monthly_price_cents=9900,
        entitlements={
            "ai.requests_per_day": 10_000,
            "ai.tokens_per_day": 5_000_000,
            "storage.bytes": 50_000_000_000,
            "agents.enabled": True,
            "knowledge.bases": 25,
            "workflows.enabled": True,
            "analytics.export": True,
        },
    ),
    "enterprise": Plan(
        id="enterprise",
        name="Enterprise",
        description="Unlimited platform access",
        monthly_price_cents=0,
        entitlements={
            "ai.requests_per_day": -1,  # unlimited
            "ai.tokens_per_day": -1,
            "storage.bytes": -1,
            "agents.enabled": True,
            "knowledge.bases": -1,
            "workflows.enabled": True,
            "analytics.export": True,
            "sso.enabled": True,
            "dedicated_support": True,
        },
    ),
}
