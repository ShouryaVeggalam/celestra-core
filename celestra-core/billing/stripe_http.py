"""Stripe checkout HTTP endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user
from auth.models import User
from billing.stripe import StripeAdapter, StripeCheckoutSession, StripeCheckoutSessionRequest
from core.container import Container, get_container
from shared.exceptions.base import ConfigurationError

router = APIRouter(prefix="/billing/stripe", tags=["billing-stripe"])


def provide_stripe(container: Annotated[Container, Depends(get_container)]) -> StripeAdapter:
    try:
        adapter = container.resolve("stripe_adapter")
    except KeyError as exc:
        raise ConfigurationError("Stripe is not configured on this deployment") from exc
    assert isinstance(adapter, StripeAdapter)
    return adapter


@router.post("/checkout", response_model=StripeCheckoutSession)
async def create_checkout(
    payload: StripeCheckoutSessionRequest,
    _: Annotated[User, Depends(get_current_user)],
    stripe: Annotated[StripeAdapter, Depends(provide_stripe)],
) -> StripeCheckoutSession:
    return await stripe.create_checkout_session(payload)
