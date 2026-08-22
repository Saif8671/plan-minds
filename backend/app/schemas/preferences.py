from datetime import time
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserPreferencesUpdate(BaseModel):
    wake_time: time | None = None
    sleep_time: time | None = None
    work_start: time | None = None
    work_end: time | None = None
    college_start: time | None = None
    college_end: time | None = None
    break_duration_minutes: int | None = Field(default=None, ge=5, le=120)
    preferred_study_time: str | None = Field(
        default=None, description="morning | afternoon | evening | night"
    )
    preferred_workout_time: str | None = Field(
        default=None, description="morning | afternoon | evening | night"
    )
    notification_preferences: dict[str, Any] | None = None
    timezone: str | None = Field(default=None, max_length=64)
    working_days: list[str] | None = None
    meals: dict[str, str] | None = Field(
        default=None, description="Preferred meal times, e.g. {'breakfast': '08:00'}"
    )
    scheduling_style: str | None = Field(default=None, description="strict | flexible")
    default_buffer_time_minutes: int | None = Field(default=None, ge=0, le=120)


class UserPreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    wake_time: time | None = None
    sleep_time: time | None = None
    work_start: time | None = None
    work_end: time | None = None
    college_start: time | None = None
    college_end: time | None = None
    break_duration_minutes: int = 15
    preferred_study_time: str | None = None
    preferred_workout_time: str | None = None
    notification_preferences: dict[str, Any] | None = None
    timezone: str = "UTC"
    working_days: list[str] | None = None
    meals: dict[str, str] | None = None
    scheduling_style: str = "flexible"
    default_buffer_time_minutes: int = 15
