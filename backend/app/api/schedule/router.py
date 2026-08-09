"""Schedule API endpoints — CRUD + block editing + AI generation + validation."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, DbSession
from app.models import ScheduleStatus
from app.schemas.base import ApiResponse, PaginatedData
from app.schemas.schedule import (
    ScheduleBlockCreate,
    ScheduleBlockMove,
    ScheduleBlockUpdate,
    ScheduleCreate,
    ScheduleGenerateMultiRequest,
    ScheduleGenerateRequest,
    ScheduleMergeRequest,
    ScheduleRegenerateRequest,
    ScheduleResponse,
    ScheduleSplitRequest,
    ScheduleUpdate,
    ValidationResultResponse,
)
from app.services.scheduling.engine import SchedulingEngine
from app.services.scheduling.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["Schedules"])

_common_responses = {
    401: {"description": "Not authenticated"},
    404: {"description": "Schedule not found"},
}


# ─── Standard CRUD ──────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ApiResponse[ScheduleResponse],
    status_code=201,
    responses={401: {"description": "Not authenticated"}},
    summary="Create a schedule",
)
async def create_schedule(
    data: ScheduleCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Manually create a schedule container. Use `/generate` for AI-powered generation."""
    service = ScheduleService(db)
    result = await service.create_schedule(current_user.id, data)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=ApiResponse[PaginatedData[ScheduleResponse]],
    responses={401: {"description": "Not authenticated"}},
    summary="List schedules",
)
async def list_schedules(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: ScheduleStatus | None = None,
):
    """Return a paginated list of the user's schedules, optionally filtered by status."""
    service = ScheduleService(db)
    skip = (page - 1) * page_size
    schedules, total = await service.get_schedules(
        current_user.id, skip, page_size, status
    )
    return ApiResponse(data=PaginatedData(
        items=schedules, total=total, page=page, page_size=page_size
    ))


@router.get(
    "/{schedule_id}",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Get a schedule",
)
async def get_schedule(
    schedule_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Return a single schedule including its generated_schedule blocks."""
    service = ScheduleService(db)
    result = await service.get_schedule(current_user.id, schedule_id)
    return ApiResponse(data=result)


@router.patch(
    "/{schedule_id}",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Update a schedule",
)
async def update_schedule(
    schedule_id: UUID,
    data: ScheduleUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update schedule metadata (title, status, etc.)."""
    service = ScheduleService(db)
    result = await service.update_schedule(current_user.id, schedule_id, data)
    return ApiResponse(data=result)


@router.delete(
    "/{schedule_id}",
    status_code=204,
    responses=_common_responses,
    summary="Delete a schedule",
)
async def delete_schedule(
    schedule_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Permanently delete a schedule and all its linked tasks."""
    service = ScheduleService(db)
    await service.delete_schedule(current_user.id, schedule_id)


# ─── Validation ────────────────────────────────────────────────────────


@router.get(
    "/{schedule_id}/validate",
    response_model=ApiResponse[ValidationResultResponse],
    responses=_common_responses,
    summary="Validate a schedule",
)
async def validate_schedule(
    schedule_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    buffer_minutes: int = Query(5, ge=0, le=60, description="Minimum buffer between blocks (minutes)"),
):
    """Run all validation rules and return conflicts/warnings without saving."""
    service = ScheduleService(db)
    result = await service.validate_schedule(current_user.id, schedule_id, buffer_minutes)
    return ApiResponse(data=result)


# ─── Block editing ──────────────────────────────────────────────────────


@router.post(
    "/{schedule_id}/blocks",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Create a schedule block",
)
async def create_schedule_block(
    schedule_id: UUID,
    data: ScheduleBlockCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Add a new block manually to an existing generated schedule.

    Validation runs before saving — returns 409 if the block creates a conflict.
    """
    service = ScheduleService(db)
    result = await service.create_block(current_user.id, schedule_id, data)
    return ApiResponse(data=result)


@router.patch(
    "/{schedule_id}/blocks/{block_id}",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Update a schedule block",
)
async def update_schedule_block(
    schedule_id: UUID,
    block_id: str,
    data: ScheduleBlockUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update a block's title, time, or category."""
    service = ScheduleService(db)
    result = await service.update_block(current_user.id, schedule_id, block_id, data)
    return ApiResponse(data=result)


@router.post(
    "/{schedule_id}/blocks/{block_id}/move",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Move a schedule block",
)
async def move_schedule_block(
    schedule_id: UUID,
    block_id: str,
    data: ScheduleBlockMove,
    current_user: CurrentUser,
    db: DbSession,
):
    """Move a block to a new start/end time. Validates for conflicts after moving."""
    service = ScheduleService(db)
    result = await service.move_block(current_user.id, schedule_id, block_id, data)
    return ApiResponse(data=result)


@router.post(
    "/{schedule_id}/blocks/{block_id}/split",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Split a schedule block",
)
async def split_schedule_block(
    schedule_id: UUID,
    block_id: str,
    data: ScheduleSplitRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Split a block at a given time, creating two contiguous sub-blocks."""
    service = ScheduleService(db)
    result = await service.split_block(current_user.id, schedule_id, block_id, data)
    return ApiResponse(data=result)


@router.post(
    "/{schedule_id}/blocks/merge",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Merge two schedule blocks",
)
async def merge_schedule_blocks(
    schedule_id: UUID,
    data: ScheduleMergeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Merge two adjacent blocks into one. Both blocks must have touching start/end times."""
    service = ScheduleService(db)
    result = await service.merge_blocks(current_user.id, schedule_id, data)
    return ApiResponse(data=result)


@router.delete(
    "/{schedule_id}/blocks/{block_id}",
    response_model=ApiResponse[ScheduleResponse],
    responses=_common_responses,
    summary="Delete a schedule block",
)
async def delete_schedule_block(
    schedule_id: UUID,
    block_id: str,
    current_user: CurrentUser,
    db: DbSession,
):
    """Remove a block from the generated schedule."""
    service = ScheduleService(db)
    result = await service.delete_block(current_user.id, schedule_id, block_id)
    return ApiResponse(data=result)


# ─── AI-powered generation ─────────────────────────────────────────────


@router.post(
    "/generate",
    response_model=ApiResponse[ScheduleResponse],
    summary="Generate a daily schedule",
)
async def generate_schedule(
    data: ScheduleGenerateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Generate an optimised daily schedule using the scoring-based engine.

    - Tasks are scored by priority, deadline urgency, preferred time, and energy level
    - Meals, work/college blocks, and fixed tasks are placed first
    - Flexible tasks fill remaining slots by highest score
    - Returns conflict suggestions if the day is overpacked
    """
    engine = SchedulingEngine(db)
    result = await engine.generate(current_user, data)
    return ApiResponse(data=result)


@router.post(
    "/generate/multi-day",
    response_model=ApiResponse[list[ScheduleResponse]],
    summary="Generate a multi-day schedule",
)
async def generate_multi_day_schedule(
    data: ScheduleGenerateMultiRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Generate schedules for multiple consecutive days (2–14)."""
    engine = SchedulingEngine(db)
    result = await engine.generate_multi_day(current_user, data)
    return ApiResponse(data=result)


@router.post(
    "/regenerate",
    response_model=ApiResponse[ScheduleResponse],
    summary="Regenerate today's schedule",
)
async def regenerate_schedule(
    data: ScheduleRegenerateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Regenerate a schedule, optionally skipping specific tasks."""
    engine = SchedulingEngine(db)
    result = await engine.regenerate(current_user, data)
    return ApiResponse(data=result)


@router.get(
    "/today/current",
    response_model=ApiResponse[ScheduleResponse],
    responses={404: {"description": "No schedule found for today"}},
    summary="Get today's schedule",
)
async def get_today_schedule(current_user: CurrentUser, db: DbSession):
    """Return the active schedule for today, if one exists."""
    engine = SchedulingEngine(db)
    schedule = await engine.get_today(current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="No schedule found for today")
    return ApiResponse(data=schedule)


@router.get(
    "/week/current",
    response_model=ApiResponse[list[ScheduleResponse]],
    summary="Get this week's schedules",
)
async def get_week_schedule(
    current_user: CurrentUser,
    db: DbSession,
    start: date | None = Query(None, description="Week start date (defaults to today)"),
):
    """Return all schedules for the current week (7 days from start date)."""
    engine = SchedulingEngine(db)
    result = await engine.get_week(current_user.id, start)
    return ApiResponse(data=result)
