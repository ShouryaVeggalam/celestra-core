"""Storage HTTP API."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from auth.dependencies import get_current_user
from auth.models import User
from core.container import Container, get_container
from shared.exceptions.base import ValidationAppError
from storage.service import StorageService
from storage.types import ObjectInfo

router = APIRouter(prefix="/storage", tags=["storage"])


def provide_storage_service(container: Annotated[Container, Depends(get_container)]) -> StorageService:
    try:
        service = container.resolve("storage_service")
    except KeyError as exc:
        raise ValidationAppError("Storage service is not initialized") from exc
    assert isinstance(service, StorageService)
    return service


class SignedUrlResponse(BaseModel):
    key: str
    url: str


@router.post("/upload", response_model=ObjectInfo)
async def upload(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[StorageService, Depends(provide_storage_service)],
    file: UploadFile = File(...),
    key: str | None = Form(default=None),
) -> ObjectInfo:
    data = await file.read()
    object_key = key or file.filename or "upload.bin"
    return await service.upload(
        object_key,
        data,
        content_type=file.content_type or "application/octet-stream",
    )


@router.get("/objects/{key:path}")
async def download(
    key: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[StorageService, Depends(provide_storage_service)],
) -> Response:
    obj = await service.download(key)
    return Response(content=obj.data, media_type=obj.info.content_type)


@router.delete("/objects/{key:path}", status_code=204)
async def delete_object(
    key: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[StorageService, Depends(provide_storage_service)],
) -> None:
    await service.delete(key)


@router.get("/objects/{key:path}/url", response_model=SignedUrlResponse)
async def signed_url(
    key: str,
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[StorageService, Depends(provide_storage_service)],
    expires_in: int = 3600,
) -> SignedUrlResponse:
    url = await service.signed_url(key, expires_in=expires_in)
    return SignedUrlResponse(key=key, url=url)


@router.get("/objects")
async def list_objects(
    _: Annotated[User, Depends(get_current_user)],
    service: Annotated[StorageService, Depends(provide_storage_service)],
    prefix: str = "",
) -> list[str]:
    return await service.list_keys(prefix=prefix)
