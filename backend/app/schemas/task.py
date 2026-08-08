from datetime import datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import RecurrenceType, TaskCategory, TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    labels: list[str] | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    category: TaskCategory = TaskCategory.OTHER
    duration: int = Field(default=60, ge=1, le=1440)
    travel_time_minutes: int = Field(default=0, ge=0, le=240)
    deadline: datetime | None = None
    reminder_time: datetime | None = None
    recurrence: RecurrenceType | None = None
    recurrence_rule: dict[str, Any] | None = None
    is_fixed: bool = False
    fixed_start: time | None = None
    fixed_end: time | None = None
    is_recurring: bool = False
    schedule_id: UUID | None = None
    status: TaskStatus = TaskStatus.PENDING


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    labels: list[str] | None = None
    priority: TaskPriority | None = None
    category: TaskCategory | None = None
    duration: int | None = Field(default=None, ge=1, le=1440)
    travel_time_minutes: int | None = Field(default=None, ge=0, le=240)
    deadline: datetime | None = None
    reminder_time: datetime | None = None
    recurrence: RecurrenceType | None = None
    recurrence_rule: dict[str, Any] | None = None
    is_fixed: bool | None = None
    fixed_start: time | None = None
    fixed_end: time | None = None
    is_recurring: bool | None = None
    completed: bool | None = None
    schedule_id: UUID | None = None
    status: TaskStatus | None = None


class TaskActivityCreate(BaseModel):
    time_spent: int = Field(ge=1, description="Time spent in minutes")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    schedule_id: UUID | None = None
    title: str
    description: str | None = None
    notes: str | None = None
    labels: list[str] | None = None
    completed: bool
    priority: TaskPriority
    category: TaskCategory
    duration: int
    travel_time_minutes: int = 0
    deadline: datetime | None = None
    reminder_time: datetime | None = None
    recurrence: RecurrenceType | None = None
    recurrence_rule: dict[str, Any] | None = None
    is_fixed: bool
    fixed_start: time | None = None
    fixed_end: time | None = None
    is_recurring: bool
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
