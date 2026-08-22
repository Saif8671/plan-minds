"""Reminders API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.base import ApiResponse
from app.schemas.reminder import (
    ReminderCreate,
    ReminderCreateRecurring,
    ReminderHistoryResponse,
    ReminderResponse,
    ReminderSnoozeRequest,
    ReminderUpdate,
)
from app.services.reminders.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["Reminders"])

_common_responses = {
    401: {"description": "Not authenticated"},
    404: {"description": "Reminder not found"},
}


@router.post(
    "",
    response_model=ApiResponse[ReminderResponse],
    status_code=201,
    summary="Create a one-time reminder",
)
async def create_reminder(
    data: ReminderCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Create a one-time reminder. For repeating reminders use `/reminders/recurring`."""
    service = ReminderService(db)
    result = await service.create_reminder(current_user.id, data)
    return ApiResponse(data=result)


@router.post(
    "/recurring",
    response_model=ApiResponse[ReminderResponse],
    status_code=201,
    summary="Create a recurring reminder",
)
async def create_recurring_reminder(
    data: ReminderCreateRecurring,
    current_user: CurrentUser,
    db: DbSession,
):
    """Create a recurring reminder (daily/weekly/monthly).

    The scheduler automatically advances `next_fire` each time it fires.
    """
    service = ReminderService(db)
    result = await service.create_recurring_reminder(current_user.id, data)
    return ApiResponse(data=result)


@router.post(
    "/generate-from-schedule/{schedule_id}",
    summary="Auto-generate reminders from schedule",
)
async def generate_from_schedule(
    schedule_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Auto-create reminders 10 minutes before each block in a generated schedule."""
    service = ReminderService(db)
    count = await service.generate_schedule_reminders(schedule_id)
    return ApiResponse(
        data={
            "created": count,
            "message": f"Created {count} reminder(s) from schedule blocks",
        }
    )


@router.get(
    "",
    response_model=ApiResponse[list[ReminderResponse]],
    summary="List reminders",
)
async def list_reminders(
    current_user: CurrentUser,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_sent: bool = True,
):
    """Return the user's reminders, optionally filtering out already-sent ones."""
    service = ReminderService(db)
    result = await service.get_reminders(current_user.id, skip, limit, include_sent)
    return ApiResponse(data=result)


@router.get(
    "/{reminder_id}/history",
    response_model=ApiResponse[list[ReminderHistoryResponse]],
    responses=_common_responses,
    summary="Get reminder fire history",
)
async def get_reminder_history(
    reminder_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(50, ge=1, le=200),
):
    """Return all fire events for a reminder: sent, snoozed, dismissed, or missed."""
    service = ReminderService(db)
    result = await service.get_reminder_history(current_user.id, reminder_id, limit)
    return ApiResponse(data=result)


@router.patch(
    "/{reminder_id}",
    response_model=ApiResponse[ReminderResponse],
    responses=_common_responses,
    summary="Update a reminder",
)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Update reminder fields."""
    service = ReminderService(db)
    result = await service.update_reminder(current_user.id, reminder_id, data)
    return ApiResponse(data=result)


@router.post(
    "/{reminder_id}/snooze",
    response_model=ApiResponse[ReminderResponse],
    responses=_common_responses,
    summary="Snooze a reminder",
)
async def snooze_reminder(
    reminder_id: UUID,
    data: ReminderSnoozeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Snooze a reminder for 1–120 minutes. Logs the snooze to history."""
    service = ReminderService(db)
    result = await service.snooze_reminder(
        current_user.id, reminder_id, data.snooze_minutes
    )
    return ApiResponse(data=result)


@router.post(
    "/{reminder_id}/complete",
    response_model=ApiResponse[ReminderResponse],
    responses=_common_responses,
    summary="Dismiss a reminder",
)
async def complete_reminder(
    reminder_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Mark a reminder as dismissed. Logs the dismissal to history."""
    service = ReminderService(db)
    result = await service.complete_reminder(current_user.id, reminder_id)
    return ApiResponse(data=result)


@router.delete(
    "/{reminder_id}",
    status_code=204,
    responses=_common_responses,
    summary="Delete a reminder",
)
async def delete_reminder(
    reminder_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """Permanently delete a reminder and its history."""
    service = ReminderService(db)
    await service.delete_reminder(current_user.id, reminder_id)
