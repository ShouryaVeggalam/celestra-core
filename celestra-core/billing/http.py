"""Billing HTTP API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from auth.models import User
from billing.service import BillingService
from billing.types import (
    AssignPlanRequest,
    EntitlementCheck,
    Plan,
    RecordUsageRequest,
    Subscription,
    UsageEvent,
    UsageSummary,
)
from core.container import Container, get_container
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/billing", tags=["billing"])


def provide_billing_service(container: Annotated[Container, Depends(get_container)]) -> BillingService:
    try:
        service = container.resolve("billing_service")
    except KeyError as exc:
        raise ValidationAppError("Billing service is not initialized") from exc
    assert isinstance(service, BillingService)
    return service


@router.get("/plans", response_model=list[Plan])
async def list_plans(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[BillingService, Depends(provide_billing_service)],
) -> list[Plan]:
    return service.list_plans()


@router.post("/subscriptions", response_model=Subscription)
async def assign_plan(
    payload: AssignPlanRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[BillingService, Depends(provide_billing_service)],
) -> Subscription:
    return service.assign_plan(payload)


@router.get("/subscriptions/{account_id}", response_model=Subscription)
async def get_subscription(
    account_id: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[BillingService, Depends(provide_billing_service)],
) -> Subscription:
    return service.get_subscription(account_id)


@router.post("/usage", response_model=UsageEvent)
async def record_usage(
    payload: RecordUsageRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[BillingService, Depends(provide_billing_service)],
) -> UsageEvent:
    return service.record_usage(payload)


@router.get("/usage/{account_id}", response_model=list[UsageSummary])
async def usage_summary(
    account_id: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[BillingService, Depends(provide_billing_service)],
    metric: str | None = None,
) -> list[UsageSummary]:
    return service.usage_summary(account_id, metric=metric)


@router.get("/entitlements/{account_id}/{feature}", response_model=EntitlementCheck)
async def check_entitlement(
    account_id: str,
    feature: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[BillingService, Depends(provide_billing_service)],
) -> EntitlementCheck:
    return service.check_entitlement(account_id, feature)
