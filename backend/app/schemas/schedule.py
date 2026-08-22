import datetime as dt
from datetime import datetime, time
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.models import ScheduleStatus, TaskCategory, TaskPriority

# ─── Schedule CRUD schemas ─────────────────────────────────────────────


class ScheduleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    start_time: datetime
    end_time: datetime
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    category: TaskCategory = TaskCategory.OTHER


class ScheduleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: ScheduleStatus | None = None
    category: TaskCategory | None = None


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    description: str | None = None
    priority: TaskPriority
    start_time: datetime
    end_time: datetime
    status: ScheduleStatus
    category: TaskCategory
    date: dt.date | None = None
    generated_schedule: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


# ─── AI parsing schemas ─────────────────────────────────────────────────


class FixedEvent(BaseModel):
    title: str
    start: time
    end: time
    category: str | None = None


class FlexibleTask(BaseModel):
    title: str
    duration: int = Field(ge=1, description="Duration in minutes")
    priority: str = "medium"
    category: str | None = None


class ParsedRoutine(BaseModel):
    wake_time: time | None = None
    sleep_time: time | None = None
    fixed_events: list[FixedEvent] = Field(default_factory=list)
    flexible_tasks: list[FlexibleTask] = Field(default_factory=list)
    notes: str | None = None


class ParseRoutineRequest(BaseModel):
    routine_text: str = Field(min_length=3, max_length=5000)
    timezone: str | None = "UTC"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    context: dict[str, Any] | None = None
    conversation_id: UUID | None = Field(
        default=None,
        description="Optional: send to a specific conversation instead of the active one",
    )


class ChatResponse(BaseModel):
    reply: str
    suggested_actions: list[str] | None = None
    actions_taken: list[str] | None = None


# ─── Schedule block schemas ──────────────────────────────────────────────


class ScheduleBlock(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    start: time
    end: time
    task_id: UUID | None = None
    category: str | None = None
    is_fixed: bool = False
    score: float | None = Field(
        default=None, description="Slot score used by the scheduler"
    )


class ScheduleBlockCreate(BaseModel):
    """Create a new block manually inside an existing generated schedule."""

    title: str = Field(min_length=1, max_length=255)
    start: time
    end: time
    category: str | None = None
    is_fixed: bool = False
    task_id: UUID | None = None


class ScheduleBlockUpdate(BaseModel):
    title: str | None = None
    start: time | None = None
    end: time | None = None
    category: str | None = None


class ScheduleBlockMove(BaseModel):
    """Move a block to a new time window."""

    new_start: time
    new_end: time


class ScheduleSplitRequest(BaseModel):
    """Split a block at a given time."""

    split_at: time = Field(
        description="Time at which to split the block (must be between block start and end)"
    )


class ScheduleMergeRequest(BaseModel):
    """Merge two adjacent blocks."""

    block_ids: list[str] = Field(
        min_length=2, max_length=2, description="Exactly 2 block IDs to merge"
    )
    merged_title: str | None = Field(
        default=None, max_length=255, description="Title for merged block"
    )


# ─── Validation schemas ──────────────────────────────────────────────────


class ConflictDetailResponse(BaseModel):
    rule: str
    message: str
    block_ids: list[str]
    severity: str  # "error" | "warning"


class ValidationResultResponse(BaseModel):
    is_valid: bool
    conflicts: list[ConflictDetailResponse]
    warnings: list[str] = Field(default_factory=list)


# ─── Schedule generation schemas ─────────────────────────────────────────


class GeneratedSchedule(BaseModel):
    date: dt.date
    wake_time: time | None = None
    sleep_time: time | None = None
    blocks: list[ScheduleBlock] = Field(default_factory=list)
    unscheduled_tasks: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] | None = None
    validation: ValidationResultResponse | None = None


class ScheduleGenerateRequest(BaseModel):
    target_date: dt.date | None = None
    include_parsed_routine: ParsedRoutine | None = None


class ScheduleGenerateMultiRequest(BaseModel):
    start_date: dt.date | None = None
    days: int = Field(default=3, ge=2, le=14)


class ScheduleRegenerateRequest(BaseModel):
    target_date: dt.date | None = None
    skipped_task_ids: list[UUID] = Field(default_factory=list)


# ─── AI Analyze schemas ──────────────────────────────────────────────────


class AIAnalyzeRequest(BaseModel):
    text: str = Field(min_length=3, max_length=5000)
    timezone: str | None = "UTC"
    auto_persist: bool = Field(
        default=False,
        description="Automatically save extracted tasks to the database",
    )


class AIAnalyzeTask(BaseModel):
    title: str
    start: str | None = None
    end: str | None = None
    duration: int | None = None
    category: str | None = None
    priority: str | None = None
    deadline: datetime | None = None
    is_recurring: bool = False
    recurrence_rule: str | None = None


class AIAnalyzeResponse(BaseModel):
    tasks: list[AIAnalyzeTask]
    wake_time: str | None = None
    sleep_time: str | None = None
    notes: str | None = None
