from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import ReminderType


class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    reminder_type: ReminderType = ReminderType.CUSTOM
    reminder_time: datetime
    task_id: UUID | None = None
    message: str | None = None


class ReminderUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    reminder_type: ReminderType | None = None
    reminder_time: datetime | None = None
    is_sent: bool | None = None
    message: str | None = None


class ReminderSnoozeRequest(BaseModel):
    snooze_minutes: int = Field(default=10, ge=1, le=120)


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    task_id: UUID | None = None
    title: str
    reminder_type: ReminderType
    reminder_time: datetime
    is_sent: bool
    is_snoozed: bool = False
    snooze_until: datetime | None = None
    is_completed: bool = False
    message: str | None = None
    created_at: datetime
