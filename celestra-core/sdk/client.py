"""
HTTP SDK client for Celestra Core — Stripe-style remote access.

Apps running outside the Core process use this client against the Core API.
"""

from __future__ import annotations

from typing import Any

import httpx


class CelestraAPIError(RuntimeError):
    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"Celestra API error {status_code}: {payload}")


class CelestraClient:
    """
    First-party HTTP client.

    Auth: pass JWT via `token=` or API key via `api_key=`.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        *,
        token: str | None = None,
        api_key: str | None = None,
        api_prefix: str = "/api/v1",
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix.rstrip("/")
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if api_key:
            headers["X-API-Key"] = api_key
        self._client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> CelestraClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def health(self) -> dict[str, Any]:
        return await self._get("/health")

    async def complete(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/ai/complete", payload)

    async def embed(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/ai/embed", payload)

    async def run_agent(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/agents/run", payload)

    async def start_workflow(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/workflows/start", payload)

    async def track(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/analytics/track", payload)

    async def record_usage(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/billing/usage", payload)

    async def list_plans(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_prefix}/billing/plans")  # type: ignore[return-value]

    async def knowledge_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/knowledge/query", payload)

    async def send_notification(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"{self.api_prefix}/notifications/send", payload)

    async def _get(self, path: str) -> Any:
        response = await self._client.get(path)
        return self._handle(response)

    async def _post(self, path: str, payload: dict[str, Any]) -> Any:
        response = await self._client.post(path, json=payload)
        return self._handle(response)

    @staticmethod
    def _handle(response: httpx.Response) -> Any:
        if response.status_code >= 400:
            try:
                payload = response.json()
            except Exception:
                payload = response.text
            raise CelestraAPIError(response.status_code, payload)
        if response.status_code == 204:
            return None
        return response.json()
