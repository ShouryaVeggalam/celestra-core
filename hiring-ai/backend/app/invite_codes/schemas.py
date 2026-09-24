from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateInviteCodeRequest(BaseModel):
    role: Literal["admin", "member"] = "member"


class InviteCodeCreatedResponse(BaseModel):
    id: str
    organization_id: str
    role: str
    code: str
    expires_at: datetime
    created_at: datetime


class InviteCodeListItem(BaseModel):
    id: str
    organization_id: str
    role: str
    status: str
    expires_at: datetime
    used_at: Optional[datetime]
    used_by_user_id: Optional[str]
    created_by_user_id: str
    created_at: datetime


class InviteCodeListResponse(BaseModel):
    items: list[InviteCodeListItem]
    total: int


class RedeemInviteCodeRequest(BaseModel):
    code: str = Field(min_length=4, max_length=32)


class RedeemInviteCodeResponse(BaseModel):
    organization_id: str
    organization_name: str
    membership_id: str
    role: str
