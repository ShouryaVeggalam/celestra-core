"""Phase 7 example — durable backends + optional cloud adapters."""

from __future__ import annotations

import asyncio

from auth.oidc import OIDCClient, OIDCSettings
from billing.stripe import StripeAdapter
from config.settings import Settings
from memory.factory import build_conversation_store, build_vector_store
from memory.types import ConversationSession, MemoryMessage
from notifications.factory import build_notification_service
from workflows.factory import build_workflow_stack


async def main() -> None:
    settings = Settings(
        memory_conversation_backend="memory",
        memory_vector_backend="memory",
        workflow_run_backend="memory",
    )
    conversations = build_conversation_store(settings, redis=None)
    vectors = build_vector_store(settings)
    engine, workflows, _ = build_workflow_stack(settings)
    notifications = build_notification_service(settings)

    session = ConversationSession(
        id="demo",
        messages=[MemoryMessage(role="user", content="phase7 ready")],
    )
    await conversations.save(session)
    print("conversation_backend", type(conversations).__name__)
    print("vector_backend", type(vectors).__name__)
    print("workflows", [w.name for w in workflows.list()])
    print("email_channel", type(notifications.senders["email"]).__name__)
    print("stripe_ready", bool(settings.stripe_secret_key))
    print("oidc_ready", bool(settings.oidc_issuer and settings.oidc_client_id))

    # Optional adapters (no network unless configured)
    if settings.stripe_secret_key:
        StripeAdapter(secret_key=settings.stripe_secret_key, price_map=settings.stripe_price_map)
    if settings.oidc_issuer and settings.oidc_client_id and settings.oidc_redirect_uri:
        client = OIDCClient(
            OIDCSettings(
                issuer=settings.oidc_issuer,
                client_id=settings.oidc_client_id,
                client_secret=settings.oidc_client_secret or "",
                redirect_uri=settings.oidc_redirect_uri,
            )
        )
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
