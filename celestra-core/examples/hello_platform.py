"""Minimal example: bootstrap Celestra Core health check."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from config.settings import get_settings
from shared.exceptions.handlers import register_exception_handlers


def main() -> None:
    settings = get_settings()
    print(f"Booting {settings.app_name} ({settings.env.value})")

    app = FastAPI(title=settings.app_name)
    register_exception_handlers(app)

    @app.get("/health")
    async def health():
        return {"status": "ok", "app": settings.app_name}

    with TestClient(app) as client:
        response = client.get("/health")
        print(response.status_code, response.json())


if __name__ == "__main__":
    main()
