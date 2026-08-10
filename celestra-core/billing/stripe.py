"""Stripe Checkout adapter — optional paid plan upgrades via Stripe API."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, Field

from shared.exceptions.base import ConfigurationError, ExternalServiceError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


class StripeCheckoutSessionRequest(BaseModel):
    account_id: str
    plan_id: str
    success_url: str
    cancel_url: str
    customer_email: str | None = None
    quantity: int = Field(default=1, ge=1)


class StripeCheckoutSession(BaseModel):
    id: str
    url: str
    account_id: str
    plan_id: str


class StripeAdapter:
    """Thin HTTP adapter for Stripe Checkout Sessions (no stripe SDK required)."""

    def __init__(
        self,
        *,
        secret_key: str,
        price_map: dict[str, str] | None = None,
        api_base: str = "https://api.stripe.com/v1",
    ) -> None:
        if not secret_key:
            raise ConfigurationError("Stripe secret key is required")
        self.secret_key = secret_key
        self.price_map = price_map or {}
        self.api_base = api_base.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.api_base,
            auth=(self.secret_key, ""),
            timeout=30.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def price_id_for_plan(self, plan_id: str) -> str:
        if plan_id not in self.price_map:
            raise ConfigurationError(
                f"No Stripe price mapped for plan '{plan_id}'. "
                "Set CELESTRA_STRIPE_PRICE_MAP as plan_id=price_xxx,..."
            )
        return self.price_map[plan_id]

    async def create_checkout_session(self, request: StripeCheckoutSessionRequest) -> StripeCheckoutSession:
        price_id = self.price_id_for_plan(request.plan_id)
        data: dict[str, Any] = {
            "mode": "subscription",
            "success_url": request.success_url,
            "cancel_url": request.cancel_url,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": str(request.quantity),
            "client_reference_id": request.account_id,
            "metadata[account_id]": request.account_id,
            "metadata[plan_id]": request.plan_id,
        }
        if request.customer_email:
            data["customer_email"] = request.customer_email
        try:
            resp = await self._client.post("/checkout/sessions", data=data)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("stripe_checkout_failed", error=str(exc))
            raise ExternalServiceError(f"Stripe checkout failed: {exc}") from exc
        payload = resp.json()
        session = StripeCheckoutSession(
            id=payload["id"],
            url=payload["url"],
            account_id=request.account_id,
            plan_id=request.plan_id,
        )
        logger.info(
            "stripe_checkout_created",
            session_id=session.id,
            account_id=request.account_id,
            plan_id=request.plan_id,
        )
        return session
