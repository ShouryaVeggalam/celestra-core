"""Conversation memory helpers — windowing, ownership, and application isolation."""

from __future__ import annotations

from memory.base import ConversationStore
from memory.types import DEFAULT_APPLICATION, ConversationSession, MemoryMessage
from providers.types import Message, Role
from shared.exceptions.base import NotFoundError, ValidationAppError
from shared.logging.setup import get_logger
from shared.utils.dates import utcnow
from shared.utils.ids import new_uuid

logger = get_logger(__name__)


def normalize_application(application: str | None) -> str:
    from config.applications import require_memory_application

    return require_memory_application(application)


class ConversationMemory:
    """High-level conversation memory API over a ConversationStore."""

    def __init__(self, store: ConversationStore, *, window_size: int = 20) -> None:
        self.store = store
        self.window_size = window_size

    @staticmethod
    def assert_access(
        session: ConversationSession,
        *,
        user_id: str,
        application: str,
    ) -> None:
        """Authorize access without disclosing foreign sessions (always NotFound)."""
        app = normalize_application(application)
        session_app = normalize_application(session.application)
        if session.user_id != user_id or session_app != app:
            logger.info(
                "memory_access_denied",
                operation="assert_access",
                session_id=session.id,
                application=app,
            )
            raise NotFoundError("Conversation session not found")

    async def get_owned(
        self,
        session_id: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> ConversationSession:
        if not user_id:
            raise ValidationAppError("user_id is required for memory operations")
        app = normalize_application(application)
        session = await self.store.get(session_id, application=app)
        if session is None:
            raise NotFoundError("Conversation session not found")
        self.assert_access(session, user_id=user_id, application=app)
        return session

    async def get_or_create(
        self,
        session_id: str | None = None,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> ConversationSession:
        if not user_id:
            raise ValidationAppError("user_id is required for memory operations")
        app = normalize_application(application)
        sid = session_id or str(new_uuid())
        existing = await self.store.get(sid, application=app)
        if existing:
            self.assert_access(existing, user_id=user_id, application=app)
            return existing
        session = ConversationSession(id=sid, user_id=user_id, application=app)
        return await self.store.save(session)

    async def add(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
        **metadata: object,
    ) -> ConversationSession:
        """Append to an existing owned session. Does not create sessions."""
        app = normalize_application(application)
        await self.get_owned(session_id, user_id=user_id, application=app)
        return await self.store.append(
            session_id,
            [MemoryMessage(role=role, content=content, metadata=dict(metadata))],  # type: ignore[arg-type]
            application=app,
        )

    async def window(
        self,
        session_id: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> list[MemoryMessage]:
        session = await self.get_owned(
            session_id, user_id=user_id, application=application
        )
        return session.messages[-self.window_size :]

    async def as_provider_messages(
        self,
        session_id: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> list[Message]:
        messages = await self.window(
            session_id, user_id=user_id, application=application
        )
        result: list[Message] = []
        for msg in messages:
            result.append(Message(role=Role(msg.role), content=msg.content))
        return result

    async def clear(
        self,
        session_id: str,
        *,
        user_id: str,
        application: str = DEFAULT_APPLICATION,
    ) -> None:
        await self.get_owned(session_id, user_id=user_id, application=application)
        await self.store.delete(
            session_id, application=normalize_application(application)
        )

    async def touch(self, session: ConversationSession) -> ConversationSession:
        session.updated_at = utcnow()
        return await self.store.save(session)
