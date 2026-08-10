"""Global exception handlers for FastAPI applications built on Celestra Core."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from shared.exceptions.base import CelestraError
from shared.logging.setup import get_logger

logger = get_logger(__name__)


def _track_error(code: str) -> None:
    try:
        from monitoring.metrics import get_metrics

        get_metrics().track_error(code)
    except Exception:
        pass


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CelestraError)
    async def celestra_error_handler(_: Request, exc: CelestraError) -> JSONResponse:
        logger.warning("celestra_error", code=exc.code, message=exc.message, details=exc.details)
        _track_error(exc.code)
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RequestValidationError)
    async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info("request_validation_error", errors=exc.errors())
        _track_error("validation_error")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": {"errors": exc.errors()},
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        _track_error("http_error")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "http_error", "message": str(exc.detail)}},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", error=str(exc))
        _track_error("internal_error")
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "An unexpected error occurred"}},
        )
