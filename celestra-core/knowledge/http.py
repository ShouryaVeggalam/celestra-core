"""Knowledge / RAG HTTP API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from knowledge.service import KnowledgeService
from knowledge.types import Document, IngestTextRequest, KnowledgeBase, QueryRequest, QueryResponse
from shared.exceptions.base import ValidationAppError

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def provide_knowledge_service(container: Annotated[Container, Depends(get_container)]) -> KnowledgeService:
    try:
        service = container.resolve("knowledge_service")
    except KeyError as exc:
        raise ValidationAppError("Knowledge service is not initialized") from exc
    assert isinstance(service, KnowledgeService)
    return service


class CreateKBRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str = ""


@router.post("/bases", response_model=KnowledgeBase)
async def create_base(
    payload: CreateKBRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[KnowledgeService, Depends(provide_knowledge_service)],
) -> KnowledgeBase:
    return service.create_knowledge_base(payload.name, payload.description)


@router.get("/bases", response_model=list[KnowledgeBase])
async def list_bases(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[KnowledgeService, Depends(provide_knowledge_service)],
) -> list[KnowledgeBase]:
    return service.list_knowledge_bases()


@router.post("/ingest", response_model=Document)
async def ingest(
    payload: IngestTextRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[KnowledgeService, Depends(provide_knowledge_service)],
) -> Document:
    return await service.ingest_text(payload)


@router.post("/query", response_model=QueryResponse)
async def query(
    payload: QueryRequest,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[KnowledgeService, Depends(provide_knowledge_service)],
) -> QueryResponse:
    return await service.query(payload)


@router.get("/bases/{name}/documents", response_model=list[Document])
async def list_documents(
    name: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[KnowledgeService, Depends(provide_knowledge_service)],
) -> list[Document]:
    return service.list_documents(name)
