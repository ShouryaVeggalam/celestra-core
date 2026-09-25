"""Groq chat completions client (OpenAI-compatible API)."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

import httpx

from app.config import Settings


class GroqError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


_JSON_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = (text or "").strip()
    fence = _JSON_FENCE.search(cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start < 0 or end <= start:
        raise GroqError("malformed_output", "Groq did not return a JSON object.")
    try:
        payload = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError as exc:
        raise GroqError("malformed_output", "Groq returned invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise GroqError("malformed_output", "Groq JSON must be an object.")
    return payload


class GroqClient:
    def __init__(self, settings: Settings, *, client: Optional[httpx.AsyncClient] = None) -> None:
        self._settings = settings
        self._client = client

    def configured(self) -> bool:
        return bool((self._settings.groq_api_key or "").strip())

    async def chat_json(
        self,
        *,
        system: str,
        user: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> dict[str, Any]:
        if not self.configured():
            raise GroqError(
                "groq_not_configured",
                "Set GROQ_API_KEY to enable AI features.",
            )
        body = {
            "model": self._settings.groq_model or "qwen/qwen3.8-27b",
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._settings.groq_api_key.strip()}",
            "Content-Type": "application/json",
        }
        url = f"{self._settings.groq_base_url.rstrip('/')}/chat/completions"
        owns = self._client is None
        http = self._client or httpx.AsyncClient(timeout=60.0)
        try:
            response = await http.post(url, headers=headers, json=body)
        finally:
            if owns:
                await http.aclose()
        if response.status_code == 401:
            raise GroqError("groq_unauthorized", "Groq rejected the API key.")
        if response.status_code == 429:
            raise GroqError("groq_rate_limited", "Groq rate limit reached. Try again shortly.")
        if response.status_code >= 400:
            raise GroqError("groq_unavailable", "Groq is temporarily unavailable.")
        payload = response.json()
        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GroqError("malformed_output", "Unexpected Groq response shape.") from exc
        return extract_json_object(str(content or ""))
