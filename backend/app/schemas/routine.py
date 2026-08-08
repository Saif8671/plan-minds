from datetime import datetime, time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import RecurrenceType, RoutineCategory, TaskPriority


class RoutineCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    routine_text: str = Field(min_length=1, max_length=5000)
    category: RoutineCategory = RoutineCategory.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    frequency: RecurrenceType | None = None
    estimated_duration: int = Field(default=60, ge=1, le=1440)
    preferred_time: time | None = None
    tags: list[str] | None = None


class RoutineUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    routine_text: str | None = Field(default=None, min_length=1, max_length=5000)
    category: RoutineCategory | None = None
    priority: TaskPriority | None = None
    frequency: RecurrenceType | None = None
    estimated_duration: int | None = Field(default=None, ge=1, le=1440)
    preferred_time: time | None = None
    tags: list[str] | None = None
    is_active: bool | None = None


class RoutineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None = None
    routine_text: str
    category: RoutineCategory
    priority: TaskPriority
    frequency: RecurrenceType | None = None
    estimated_duration: int
    preferred_time: time | None = None
    tags: list[str] | None = None
    parsed_data: dict[str, Any] | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
