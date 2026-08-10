"""
In-process SDK — product apps embedded with Core services.

Prefer this when the app shares the same Python process / container.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.service import AgentService
from agents.types import AgentRunRequest, AgentRunResult
from ai.schemas import CompleteRequest, CompleteResponse, EmbedRequest, EmbedResponse
from ai.service import AIService
from analytics.service import AnalyticsService
from analytics.types import AnalyticsEvent, TrackEventRequest
from billing.service import BillingService
from billing.types import EntitlementCheck, RecordUsageRequest, UsageEvent
from core.container import Container, get_container
from knowledge.service import KnowledgeService
from knowledge.types import IngestTextRequest, QueryRequest, QueryResponse
from memory.service import MemoryService
from notifications.service import NotificationService
from notifications.types import Notification, SendNotificationRequest
from storage.service import StorageService
from workflows.service import WorkflowService
from workflows.types import StartWorkflowRequest, WorkflowRun


@dataclass
class CelestraSDK:
    """Typed in-process facade over Core platform services."""

    ai: AIService
    memory: MemoryService
    agents: AgentService
    workflows: WorkflowService
    storage: StorageService
    notifications: NotificationService
    knowledge: KnowledgeService
    billing: BillingService
    analytics: AnalyticsService

    @classmethod
    def from_container(cls, container: Container | None = None) -> CelestraSDK:
        c = container or get_container()

        def req(name: str) -> Any:
            return c.resolve(name)

        return cls(
            ai=req("ai_service"),
            memory=req("memory_service"),
            agents=req("agent_service"),
            workflows=req("workflow_service"),
            storage=req("storage_service"),
            notifications=req("notification_service"),
            knowledge=req("knowledge_service"),
            billing=req("billing_service"),
            analytics=req("analytics_service"),
        )

    async def complete(self, request: CompleteRequest) -> CompleteResponse:
        result = await self.ai.complete(request)
        self.analytics.track(
            TrackEventRequest(name="ai.complete", properties={"model": result.model, "provider": result.provider})
        )
        self.billing.record_usage(
            RecordUsageRequest(
                account_id="default",
                metric="ai.requests_per_day",
                quantity=1,
                properties={"model": result.model},
            )
        )
        return result

    async def embed(self, request: EmbedRequest) -> EmbedResponse:
        return await self.ai.embed(request)

    async def run_agent(self, request: AgentRunRequest) -> AgentRunResult:
        result = await self.agents.run(request)
        self.analytics.track(
            TrackEventRequest(name="agent.run", properties={"agent": result.agent, "steps": len(result.steps)})
        )
        return result

    async def start_workflow(self, request: StartWorkflowRequest) -> WorkflowRun:
        run = await self.workflows.start(request)
        self.analytics.track(
            TrackEventRequest(name="workflow.start", properties={"workflow": run.workflow, "status": run.status.value})
        )
        return run

    async def query_knowledge(self, request: QueryRequest) -> QueryResponse:
        return await self.knowledge.query(request)

    async def ingest_knowledge(self, request: IngestTextRequest):
        return await self.knowledge.ingest_text(request)

    async def notify(self, request: SendNotificationRequest) -> Notification:
        return await self.notifications.send(request)

    def track(self, request: TrackEventRequest) -> AnalyticsEvent:
        return self.analytics.track(request)

    def record_usage(self, request: RecordUsageRequest) -> UsageEvent:
        return self.billing.record_usage(request)

    def check_entitlement(self, account_id: str, feature: str) -> EntitlementCheck:
        return self.billing.check_entitlement(account_id, feature)
