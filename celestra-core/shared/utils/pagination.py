"""Pagination primitives shared across APIs."""

from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


def paginate_sequence(items: Sequence[T], params: PageParams) -> PageResult[T]:
    total = len(items)
    slice_ = list(items[params.offset : params.offset + params.limit])
    return PageResult(items=slice_, total=total, page=params.page, page_size=params.page_size)
