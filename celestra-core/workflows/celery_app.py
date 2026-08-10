"""Celery application factory — foundation wiring for durable workflow workers."""

from __future__ import annotations

from celery import Celery

from config.settings import Settings, get_settings


def create_celery_app(settings: Settings | None = None) -> Celery:
    cfg = settings or get_settings()
    app = Celery(
        "celestra_core",
        broker=cfg.celery_broker_url,
        backend=cfg.celery_result_backend,
    )
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
    )
    return app


celery_app = create_celery_app()
