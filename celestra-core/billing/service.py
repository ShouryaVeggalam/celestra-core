"""Billing facade — plans, subscriptions, metering, entitlements."""

from __future__ import annotations

from billing.plans import DEFAULT_PLANS
from billing.store import BillingStore
from billing.types import (
    AssignPlanRequest,
    EntitlementCheck,
    Plan,
    RecordUsageRequest,
    Subscription,
    UsageEvent,
    UsageSummary,
)
from shared.exceptions.base import ForbiddenError, NotFoundError, ValidationAppError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class BillingService:
    def __init__(self, store: BillingStore | None = None, *, default_plan_id: str = "free") -> None:
        self.store = store or BillingStore()
        self.plans = dict(DEFAULT_PLANS)
        self.default_plan_id = default_plan_id

    def list_plans(self) -> list[Plan]:
        return sorted(self.plans.values(), key=lambda p: p.monthly_price_cents)

    def get_plan(self, plan_id: str) -> Plan:
        if plan_id not in self.plans:
            raise NotFoundError(f"Plan '{plan_id}' not found")
        return self.plans[plan_id].model_copy(deep=True)

    def assign_plan(self, request: AssignPlanRequest) -> Subscription:
        plan = self.get_plan(request.plan_id)
        sub = Subscription(account_id=request.account_id, plan_id=plan.id)
        saved = self.store.set_subscription(sub)
        logger.info("plan_assigned", account_id=request.account_id, plan_id=plan.id)
        return saved

    def get_subscription(self, account_id: str) -> Subscription:
        sub = self.store.get_subscription(account_id)
        if sub is None:
            return self.assign_plan(AssignPlanRequest(account_id=account_id, plan_id=self.default_plan_id))
        return sub

    def record_usage(self, request: RecordUsageRequest) -> UsageEvent:
        if request.quantity < 0:
            raise ValidationAppError("quantity must be >= 0")
        # Ensure subscription exists
        self.get_subscription(request.account_id)
        event = UsageEvent(
            account_id=request.account_id,
            metric=request.metric,
            quantity=request.quantity,
            unit=request.unit,
            properties=request.properties,
        )
        saved = self.store.add_usage(event)
        logger.info(
            "usage_recorded",
            account_id=request.account_id,
            metric=request.metric,
            quantity=request.quantity,
        )
        try:
            from monitoring.metrics import get_metrics

            get_metrics().billing_usage_total.labels(metric=request.metric).inc(request.quantity)
        except Exception:
            pass
        return saved

    def usage_summary(self, account_id: str, metric: str | None = None) -> list[UsageSummary]:
        self.get_subscription(account_id)
        return self.store.summarize(account_id, metric=metric)

    def check_entitlement(self, account_id: str, feature: str) -> EntitlementCheck:
        sub = self.get_subscription(account_id)
        plan = self.get_plan(sub.plan_id)
        if feature not in plan.entitlements:
            return EntitlementCheck(
                account_id=account_id,
                feature=feature,
                allowed=False,
                plan_id=plan.id,
            )

        limit = plan.entitlements[feature]
        if isinstance(limit, bool):
            return EntitlementCheck(
                account_id=account_id,
                feature=feature,
                allowed=limit,
                limit=limit,
                plan_id=plan.id,
            )

        if isinstance(limit, str):
            return EntitlementCheck(
                account_id=account_id,
                feature=feature,
                allowed=True,
                limit=limit,
                plan_id=plan.id,
            )

        # numeric limit: -1 means unlimited
        usage = self.store.metric_total(account_id, feature)
        if limit < 0:
            return EntitlementCheck(
                account_id=account_id,
                feature=feature,
                allowed=True,
                limit=limit,
                usage=usage,
                remaining=None,
                plan_id=plan.id,
            )
        remaining = max(float(limit) - usage, 0.0)
        return EntitlementCheck(
            account_id=account_id,
            feature=feature,
            allowed=usage < float(limit),
            limit=limit,
            usage=usage,
            remaining=remaining,
            plan_id=plan.id,
        )

    def require_entitlement(self, account_id: str, feature: str) -> EntitlementCheck:
        check = self.check_entitlement(account_id, feature)
        if not check.allowed:
            raise ForbiddenError(
                f"Plan entitlement '{feature}' denied",
                details=check.model_dump(),
            )
        return check
