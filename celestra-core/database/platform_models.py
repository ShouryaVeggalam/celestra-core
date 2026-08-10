"""Durable platform tables — vectors, billing, analytics, knowledge metadata."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class VectorRecordModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "platform_vector_records"

    namespace: Mapped[str] = mapped_column(String(128), nullable=False, index=True, default="default")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[Any]] = mapped_column(JSONB, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class BillingSubscriptionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "billing_subscriptions"
    __table_args__ = (UniqueConstraint("account_id", name="uq_billing_subscriptions_account_id"),)

    account_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)


class BillingUsageEventModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "billing_usage_events"

    account_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    metric: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="count")
    properties: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)


class AnalyticsEventModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "analytics_events"

    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    account_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    properties: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class KnowledgeBaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_bases"
    __table_args__ = (UniqueConstraint("name", name="uq_knowledge_bases_name"),)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    document_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class KnowledgeDocumentModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "knowledge_documents"

    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, nullable=False, default=dict)
