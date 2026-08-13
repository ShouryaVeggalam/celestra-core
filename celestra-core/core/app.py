"""Application factory for Celestra Core."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.builtin import register_builtin_tools
from agents.http import router as agents_router
from agents.runtime import AgentRegistry, AgentRuntime
from agents.service import AgentService
from agents.tools import ToolRegistry
from agents.types import AgentSpec
from ai.http import router as ai_router
from ai.router import ModelRouter
from ai.service import AIService
from analytics.http import router as analytics_router
from analytics.service import AnalyticsService
from auth.bridge_http import router as bridge_router
from auth.oidc import OIDCClient, OIDCSettings
from auth.oidc_http import router as oidc_router
from auth.router import router as auth_router
from auth.seed import seed_rbac
from billing.http import router as billing_router
from billing.service import BillingService
from billing.stripe import StripeAdapter
from billing.stripe_http import router as stripe_router
from config.settings import Settings, get_settings
from core.container import build_container, reset_container
from core.health import router as health_router
from database.session import async_session_factory, dispose_async_engine, init_async_engine
from knowledge.http import router as knowledge_router
from knowledge.service import KnowledgeService
from memory.conversation import ConversationMemory
from memory.factory import build_conversation_store, build_vector_store
from memory.http import router as memory_router
from memory.service import MemoryService
from monitoring.metrics import init_metrics
from monitoring.middleware import MonitoringMiddleware
from monitoring.router import router as monitoring_router
from notifications.factory import build_notification_service
from notifications.http import router as notifications_router
from prompts.loader import build_prompt_registry
from providers.factory import build_provider_registry
from shared.exceptions.handlers import register_exception_handlers
from shared.logging.setup import configure_logging, get_logger
from shared.middleware.performance import PerformanceMiddleware
from shared.middleware.request_context import RequestContextMiddleware
from shared.redis.client import close_redis, init_redis
from storage.factory import build_object_store
from storage.http import router as storage_router
from storage.service import StorageService
from workflows.bootstrap import build_workflow_stack
from workflows.http import router as workflows_router
from workflows.service import WorkflowService

logger = get_logger(__name__)
PLATFORM_VERSION = "0.8.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(settings)
    logger.info(
        "starting_celestra_core",
        env=settings.env.value,
        app=settings.app_name,
        version=PLATFORM_VERSION,
    )

    container = build_container(settings)
    init_async_engine(settings)
    redis = await init_redis(settings)
    container.redis = redis
    container.wire_cache()

    metrics = init_metrics(settings.metrics_namespace)
    metrics.set_app_info(app=settings.app_name, env=settings.env.value, version=PLATFORM_VERSION)
    container.register("metrics", metrics)

    # Phase 3 — AI
    provider_registry = build_provider_registry(settings)
    prompt_registry = build_prompt_registry()
    default_provider = settings.ai_default_provider
    if not provider_registry.has(default_provider):
        default_provider = "mock" if provider_registry.has("mock") else provider_registry.list()[0]
    model_router = ModelRouter(provider_registry, default_provider=default_provider)
    ai_service = AIService(
        registry=provider_registry,
        router=model_router,
        prompts=prompt_registry,
        default_model=settings.ai_default_model,
    )
    container.register("provider_registry", provider_registry)
    container.register("prompt_registry", prompt_registry)
    container.register("ai_service", ai_service)

    # Phase 4 + 7 — Memory / Agents / Workflows (durable backends optional)
    # Fail closed: redis backend requires a live Redis (no silent in-memory fallback).
    if settings.memory_conversation_backend == "redis":
        from shared.exceptions.base import ConfigurationError

        try:
            redis_ok = await redis.ping()
        except Exception as exc:  # noqa: BLE001
            raise ConfigurationError(
                "CELESTRA_MEMORY_CONVERSATION_BACKEND=redis but Redis is unreachable",
                details={"backend": "redis"},
            ) from exc
        if not redis_ok:
            raise ConfigurationError(
                "CELESTRA_MEMORY_CONVERSATION_BACKEND=redis but Redis ping failed",
                details={"backend": "redis"},
            )
    conversation_store = build_conversation_store(settings, redis)
    vector_store = build_vector_store(settings, namespace="memory")
    conversation_memory = ConversationMemory(
        conversation_store,
        window_size=settings.memory_window_size,
    )
    memory_service = MemoryService(
        conversations=conversation_memory,
        vectors=vector_store,
        ai=ai_service,
    )
    container.register("memory_service", memory_service)

    tool_registry = ToolRegistry()
    register_builtin_tools(tool_registry)
    agent_registry = AgentRegistry()
    agent_registry.register(
        AgentSpec(
            name="assistant",
            description="General-purpose Celestra assistant with built-in tools",
            system_prompt=(
                "You are the Celestra platform assistant. "
                "When you need a tool, reply with: CALL <tool_name> <json_arguments>"
            ),
            tools=["echo", "current_time", "add"],
            max_steps=settings.agent_max_steps_default,
        )
    )
    agent_registry.register(
        AgentSpec(
            name="echo_agent",
            description="Simple agent that prefers the echo tool",
            system_prompt="Echo useful information using the echo tool when asked.",
            tools=["echo"],
            max_steps=3,
        )
    )
    agent_runtime = AgentRuntime(
        ai=ai_service,
        tools=tool_registry,
        agents=agent_registry,
        memory=memory_service,
    )
    container.register(
        "agent_service",
        AgentService(agent_runtime, agent_registry, tool_registry),
    )

    engine, workflow_registry, _handlers = build_workflow_stack(settings, redis)
    container.register(
        "workflow_service",
        WorkflowService(
            engine=engine,
            workflows=workflow_registry,
            store=engine.store,
            celery_enabled=settings.workflow_celery_enabled,
        ),
    )

    # Phase 5 — Storage / Notifications / Knowledge
    object_store = build_object_store(settings)
    storage_service = StorageService(object_store)
    container.register("storage_service", storage_service)

    notification_service = build_notification_service(settings)
    container.register("notification_service", notification_service)

    knowledge_vectors = build_vector_store(settings, namespace="knowledge")
    knowledge_service = KnowledgeService(
        ai=ai_service,
        vectors=knowledge_vectors,
        storage=storage_service,
        chunk_size=settings.knowledge_chunk_size,
        chunk_overlap=settings.knowledge_chunk_overlap,
    )
    container.register("knowledge_service", knowledge_service)

    # Phase 6 — Billing / Analytics
    billing_service = BillingService(default_plan_id=settings.billing_default_plan)
    container.register("billing_service", billing_service)
    analytics_service = AnalyticsService()
    container.register("analytics_service", analytics_service)

    # Phase 7 — Stripe / OIDC (optional)
    stripe_adapter: StripeAdapter | None = None
    if settings.stripe_secret_key:
        stripe_adapter = StripeAdapter(
            secret_key=settings.stripe_secret_key,
            price_map=settings.stripe_price_map,
        )
        container.register("stripe_adapter", stripe_adapter)

    oidc_client: OIDCClient | None = None
    if settings.oidc_issuer and settings.oidc_client_id and settings.oidc_redirect_uri:
        oidc_client = OIDCClient(
            OIDCSettings(
                issuer=settings.oidc_issuer,
                client_id=settings.oidc_client_id,
                client_secret=settings.oidc_client_secret or "",
                redirect_uri=settings.oidc_redirect_uri,
                scopes=settings.oidc_scopes,
            )
        )
        container.register("oidc_client", oidc_client)

    logger.info(
        "phase7_ready",
        storage=object_store.name,
        memory_conversation=settings.memory_conversation_backend,
        memory_vector=settings.memory_vector_backend,
        workflow_runs=settings.workflow_run_backend,
        stripe=bool(stripe_adapter),
        oidc=bool(oidc_client),
        smtp=bool(settings.smtp_host),
        plans=[p.id for p in billing_service.list_plans()],
        notification_channels=sorted(notification_service.senders),
    )

    try:
        factory = async_session_factory()
        async with factory() as session:
            await seed_rbac(session)
            await session.commit()
        logger.info("auth_rbac_seeded")
    except Exception as exc:
        logger.warning("auth_rbac_seed_skipped", error=str(exc))

    logger.info("celestra_core_ready")
    try:
        yield
    finally:
        logger.info("shutting_down_celestra_core")
        try:
            await provider_registry.aclose()
        except Exception:
            pass
        if stripe_adapter is not None:
            try:
                await stripe_adapter.aclose()
            except Exception:
                pass
        if oidc_client is not None:
            try:
                await oidc_client.aclose()
            except Exception:
                pass
        webhook = notification_service.senders.get("webhook")
        if webhook is not None and hasattr(webhook, "aclose"):
            try:
                await webhook.aclose()
            except Exception:
                pass
        if hasattr(object_store, "aclose"):
            try:
                await object_store.aclose()
            except Exception:
                pass
        await close_redis()
        await dispose_async_engine()
        reset_container()


def create_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    app = FastAPI(
        title=cfg.app_name,
        version=PLATFORM_VERSION,
        debug=cfg.debug,
        lifespan=lifespan,
        docs_url="/docs" if not cfg.is_production else None,
        redoc_url="/redoc" if not cfg.is_production else None,
    )
    app.state.settings = cfg

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if cfg.metrics_enabled:
        app.add_middleware(MonitoringMiddleware)
    app.add_middleware(
        PerformanceMiddleware,
        enabled=cfg.log_performance,
        slow_threshold_ms=cfg.slow_request_ms,
    )
    app.add_middleware(RequestContextMiddleware, log_requests=cfg.log_requests)

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(monitoring_router)
    app.include_router(auth_router, prefix=cfg.api_prefix)
    app.include_router(bridge_router, prefix=cfg.api_prefix)
    app.include_router(oidc_router, prefix=cfg.api_prefix)
    app.include_router(ai_router, prefix=cfg.api_prefix)
    app.include_router(memory_router, prefix=cfg.api_prefix)
    app.include_router(agents_router, prefix=cfg.api_prefix)
    app.include_router(workflows_router, prefix=cfg.api_prefix)
    app.include_router(storage_router, prefix=cfg.api_prefix)
    app.include_router(notifications_router, prefix=cfg.api_prefix)
    app.include_router(knowledge_router, prefix=cfg.api_prefix)
    app.include_router(billing_router, prefix=cfg.api_prefix)
    app.include_router(stripe_router, prefix=cfg.api_prefix)
    app.include_router(analytics_router, prefix=cfg.api_prefix)

    return app
