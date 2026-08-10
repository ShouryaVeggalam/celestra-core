"""Minimal CLI entrypoint for local development."""

from __future__ import annotations

import argparse

import uvicorn

from config.settings import get_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Celestra Core platform server")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    uvicorn.run(
        "core.app:create_app",
        factory=True,
        host=args.host or settings.host,
        port=args.port or settings.port,
        reload=args.reload or settings.is_development,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
