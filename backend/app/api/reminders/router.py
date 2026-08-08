from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderSnoozeRequest,
    ReminderUpdate,
)
from app.services.reminders.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.post("", response_model=ReminderResponse, status_code=201)
async def create_reminder(
    data: ReminderCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ReminderService(db)
    return await service.create_reminder(current_user.id, data)


@router.get("", response_model=list[ReminderResponse])
async def list_reminders(
    current_user: CurrentUser,
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_sent: bool = True,
):
    service = ReminderService(db)
    return await service.get_reminders(current_user.id, skip, limit, include_sent)


@router.patch("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ReminderService(db)
    return await service.update_reminder(current_user.id, reminder_id, data)


@router.post("/{reminder_id}/snooze", response_model=ReminderResponse)
async def snooze_reminder(
    reminder_id: UUID,
    data: ReminderSnoozeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ReminderService(db)
    return await service.snooze_reminder(
        current_user.id, reminder_id, data.snooze_minutes
    )


@router.post("/{reminder_id}/complete", response_model=ReminderResponse)
async def complete_reminder(
    reminder_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ReminderService(db)
    return await service.complete_reminder(current_user.id, reminder_id)


@router.delete("/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ReminderService(db)
    await service.delete_reminder(current_user.id, reminder_id)
