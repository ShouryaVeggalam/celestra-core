"""
HTTP SDK client for Celestra Core — public product integration surface.

Product backends call Core over HTTP. Do not import Core internal modules.
Do not persist Core JWTs. Do not expose Core credentials to browsers.
"""

from __future__ import annotations

from typing import Any

import httpx

# Controlled failure categories for product backends.
ERROR_DISABLED = "disabled"
ERROR_INVALID_CONFIG = "invalid_config"
ERROR_TIMEOUT = "timeout"
ERROR_UNAVAILABLE = "unavailable"
ERROR_AUTH = "auth_error"
ERROR_INVALID_RESPONSE = "invalid_response"
ERROR_SERVER = "server_error"
ERROR_CLIENT = "client_error"
ERROR_NOT_FOUND = "not_found"
ERROR_CONFLICT = "conflict"
ERROR_VALIDATION = "validation_error"


class CelestraAPIError(RuntimeError):
    """Raised when Core returns an HTTP error or the transport fails."""

    def __init__(
        self,
        status_code: int | None,
        payload: Any,
        *,
        category: str = ERROR_SERVER,
        message: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.category = category
        detail = message or f"Celestra API error {status_code}: {payload}"
        super().__init__(detail)


class CelestraClient:
    """
    Official thin HTTP client for product backends.

    Auth:
      - ``api_key=`` → ``X-API-Key`` (service principal: AI, bridge exchange, …)
      - ``token=`` constructor default OR per-call ``token=`` (end-user Core JWT for memory)

    Core JWTs passed per-call are never stored on the client instance beyond the
    optional constructor default (products should prefer per-call tokens).
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        *,
        token: str | None = None,
        api_key: str | None = None,
        api_prefix: str = "/api/v1",
        timeout: float = 30.0,
        default_request_id: str | None = None,
    ) -> None:
        if not base_url or not str(base_url).strip():
            raise CelestraAPIError(
                None,
                None,
                category=ERROR_INVALID_CONFIG,
                message="base_url is required",
            )
        self.base_url = base_url.rstrip("/")
        self.api_prefix = api_prefix.rstrip("/") or "/api/v1"
        self._token = token
        self._api_key = api_key
        self._timeout = timeout
        self._default_request_id = default_request_id
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> CelestraClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    # --- Ops ---

    async def health(self, *, request_id: str | None = None) -> dict[str, Any]:
        return await self._request("GET", "/health", request_id=request_id, auth=False)

    async def ready(self, *, request_id: str | None = None) -> dict[str, Any]:
        return await self._request("GET", "/ready", request_id=request_id, auth=False)

    # --- AI ---

    async def complete(
        self,
        payload: dict[str, Any],
        *,
        token: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{self.api_prefix}/ai/complete",
            json=payload,
            token=token,
            request_id=request_id,
        )

    async def embed(
        self,
        payload: dict[str, Any],
        *,
        token: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{self.api_prefix}/ai/embed",
            json=payload,
            token=token,
            request_id=request_id,
        )

    async def render_prompt(
        self,
        payload: dict[str, Any],
        *,
        token: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{self.api_prefix}/ai/prompts/render",
            json=payload,
            token=token,
            request_id=request_id,
        )

    # --- Memory (requires end-user Core JWT — never fall back to shared API key) ---

    async def start_session(
        self,
        *,
        application: str,
        session_id: str | None = None,
        token: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"application": application}
        if session_id is not None:
            body["session_id"] = session_id
        return await self._request(
            "POST",
            f"{self.api_prefix}/memory/sessions",
            json=body,
            token=token,
            request_id=request_id,
            require_user_token=True,
        )

    async def add_message(
        self,
        *,
        session_id: str,
        content: str,
        application: str,
        role: str = "user",
        token: str | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{self.api_prefix}/memory/messages",
            json={
                "session_id": session_id,
                "content": content,
                "role": role,
                "application": application,
            },
            token=token,
            request_id=request_id,
            require_user_token=True,
        )

    async def get_messages(
        self,
        session_id: str,
        *,
        application: str,
        token: str | None = None,
        request_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self._request(  # type: ignore[return-value]
            "GET",
            f"{self.api_prefix}/memory/sessions/{session_id}/messages",
            params={"application": application},
            token=token,
            request_id=request_id,
            require_user_token=True,
        )

    # --- Identity bridge (service API key; Core issues the JWT) ---

    async def bridge_exchange(
        self,
        assertion: str,
        *,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"{self.api_prefix}/auth/bridge/exchange",
            json={"assertion": assertion},
            request_id=request_id,
            require_api_key=True,
        )

    # --- Optional platform helpers (unchanged) ---

    async def run_agent(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return await self._request(
            "POST", f"{self.api_prefix}/agents/run", json=payload, **kwargs
        )

    async def start_workflow(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return await self._request(
            "POST", f"{self.api_prefix}/workflows/start", json=payload, **kwargs
        )

    async def track(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return await self._request(
            "POST", f"{self.api_prefix}/analytics/track", json=payload, **kwargs
        )

    async def record_usage(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return await self._request(
            "POST", f"{self.api_prefix}/billing/usage", json=payload, **kwargs
        )

    async def list_plans(self, **kwargs: Any) -> list[dict[str, Any]]:
        return await self._request(  # type: ignore[return-value]
            "GET", f"{self.api_prefix}/billing/plans", **kwargs
        )

    async def knowledge_query(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return await self._request(
            "POST", f"{self.api_prefix}/knowledge/query", json=payload, **kwargs
        )

    async def send_notification(self, payload: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        return await self._request(
            "POST", f"{self.api_prefix}/notifications/send", json=payload, **kwargs
        )

    # --- Internals ---

    def _resolve_headers(
        self,
        *,
        token: str | None,
        request_id: str | None,
        auth: bool,
        require_user_token: bool,
        require_api_key: bool,
    ) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        rid = request_id or self._default_request_id
        if rid:
            headers["X-Request-ID"] = rid

        if not auth:
            return headers

        user_token = token if token is not None else self._token
        if require_user_token:
            if not user_token:
                raise CelestraAPIError(
                    None,
                    None,
                    category=ERROR_INVALID_CONFIG,
                    message="end-user Core JWT (token) is required for memory operations",
                )
            headers["Authorization"] = f"Bearer {user_token}"
            return headers

        if require_api_key:
            if not self._api_key:
                raise CelestraAPIError(
                    None,
                    None,
                    category=ERROR_INVALID_CONFIG,
                    message="api_key is required for bridge_exchange",
                )
            headers["X-API-Key"] = self._api_key
            return headers

        # Default: prefer explicit per-call token, else constructor token, else API key.
        if user_token:
            headers["Authorization"] = f"Bearer {user_token}"
        elif self._api_key:
            headers["X-API-Key"] = self._api_key
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        token: str | None = None,
        request_id: str | None = None,
        auth: bool = True,
        require_user_token: bool = False,
        require_api_key: bool = False,
    ) -> Any:
        headers = self._resolve_headers(
            token=token,
            request_id=request_id,
            auth=auth,
            require_user_token=require_user_token,
            require_api_key=require_api_key,
        )
        try:
            response = await self._client.request(
                method,
                path,
                json=json,
                params=params,
                headers=headers,
            )
        except httpx.TimeoutException as exc:
            raise CelestraAPIError(
                None, None, category=ERROR_TIMEOUT, message="Celestra Core request timed out"
            ) from exc
        except httpx.HTTPError as exc:
            raise CelestraAPIError(
                None,
                None,
                category=ERROR_UNAVAILABLE,
                message="Celestra Core is unavailable",
            ) from exc
        return self._handle(response)

    @staticmethod
    def _handle(response: httpx.Response) -> Any:
        if response.status_code >= 400:
            try:
                payload: Any = response.json()
            except Exception:
                payload = response.text
            raise CelestraAPIError(
                response.status_code,
                payload,
                category=_category_for_status(response.status_code),
            )
        if response.status_code == 204:
            return None
        try:
            return response.json()
        except Exception as exc:
            raise CelestraAPIError(
                response.status_code,
                response.text,
                category=ERROR_INVALID_RESPONSE,
                message="Celestra Core returned a non-JSON response",
            ) from exc


def _category_for_status(status: int) -> str:
    if status in {401, 403}:
        return ERROR_AUTH
    if status == 404:
        return ERROR_NOT_FOUND
    if status == 409:
        return ERROR_CONFLICT
    if status == 422:
        return ERROR_VALIDATION
    if status == 503:
        return ERROR_UNAVAILABLE
    if 400 <= status < 500:
        return ERROR_CLIENT
    return ERROR_SERVER
