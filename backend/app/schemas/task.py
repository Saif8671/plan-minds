from datetime import date, datetime, time
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
    recurrence: RecurrenceType | None = None
    recurrence_rule: dict[str, Any] | None = None
    is_fixed: bool = False
    fixed_start: time | None = None
    fixed_end: time | None = None
    is_recurring: bool = False

    # These fields will be used to generate the first TaskOccurrence
    duration: int = Field(default=60, ge=1, le=1440)
    travel_time_minutes: int = Field(default=0, ge=0, le=240)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    notes: str | None = None
    labels: list[str] | None = None
    priority: TaskPriority | None = None
    category: TaskCategory | None = None
    recurrence: RecurrenceType | None = None
    recurrence_rule: dict[str, Any] | None = None
    is_fixed: bool | None = None
    fixed_start: time | None = None
    fixed_end: time | None = None
    is_recurring: bool | None = None
    status: TaskStatus | None = None
    completed: bool | None = None
    duration: int | None = None
    travel_time_minutes: int | None = None
    deadline: datetime | None = None
    reminder_time: datetime | None = None


class TaskOccurrenceUpdate(BaseModel):
    status: TaskStatus | None = None
    duration: int | None = Field(default=None, ge=1, le=1440)
    travel_time_minutes: int | None = Field(default=None, ge=0, le=240)
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None


class TaskSkipRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=512, description="Optional reason for skipping")


class TaskActivityCreate(BaseModel):
    time_spent: int = Field(ge=1, description="Time spent in minutes")


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None = None
    notes: str | None = None
    labels: list[str] | None = None
    priority: TaskPriority
    category: TaskCategory
    recurrence: RecurrenceType | None = None
    recurrence_rule: dict[str, Any] | None = None
    is_fixed: bool
    fixed_start: time | None = None
    fixed_end: time | None = None
    is_recurring: bool
    duration: int = 60
    travel_time_minutes: int = 0
    deadline: datetime | None = None
    completed: bool = False
    status: TaskStatus = TaskStatus.PENDING
    reminder_time: datetime | None = None
    created_at: datetime
    updated_at: datetime


class TaskOccurrenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    user_id: UUID
    date: date
    status: TaskStatus
    duration: int
    travel_time_minutes: int
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    created_at: datetime
    updated_at: datetime
    task: TaskResponse | None = None

