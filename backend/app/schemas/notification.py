from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models import NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    message: str | None = None
    notification_type: NotificationType
    is_read: bool
    data: dict[str, Any] | None = None
    created_at: datetime


class NotificationMarkReadRequest(BaseModel):
    is_read: bool = True


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


class PushSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    endpoint: str
    created_at: datetime
