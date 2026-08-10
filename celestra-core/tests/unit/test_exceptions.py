"""Unit tests — exception handlers."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.exceptions.base import NotFoundError
from shared.exceptions.handlers import register_exception_handlers


def test_celestra_error_handler():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    async def boom():
        raise NotFoundError("missing thing")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "not_found"
    assert "missing thing" in body["error"]["message"]
