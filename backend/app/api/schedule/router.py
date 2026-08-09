from datetime import date
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, DbSession
from app.models import ScheduleStatus
from app.schemas.auth import PaginatedResponse
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleGenerateRequest,
    ScheduleGenerateMultiRequest,
    ScheduleRegenerateRequest,
    ScheduleResponse,
    ScheduleUpdate,
    ScheduleBlockUpdate,
)
from app.services.scheduling.engine import SchedulingEngine
from app.services.scheduling.schedule_service import ScheduleService

router = APIRouter(prefix="/schedules", tags=["Schedules"])


# ─── Standard CRUD ──────────────────────────────────────────────────────


@router.post("", response_model=ScheduleResponse, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ScheduleService(db)
    return await service.create_schedule(current_user.id, data)


@router.get("", response_model=PaginatedResponse[ScheduleResponse])
async def list_schedules(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: ScheduleStatus | None = None,
):
    service = ScheduleService(db)
    skip = (page - 1) * page_size
    schedules, total = await service.get_schedules(
        current_user.id, skip, page_size, status
    )
    return PaginatedResponse(
        items=schedules, total=total, page=page, page_size=page_size
    )


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ScheduleService(db)
    return await service.get_schedule(current_user.id, schedule_id)


@router.patch("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    data: ScheduleUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ScheduleService(db)
    return await service.update_schedule(current_user.id, schedule_id, data)


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ScheduleService(db)
    await service.delete_schedule(current_user.id, schedule_id)


@router.patch("/{schedule_id}/blocks/{block_id}", response_model=ScheduleResponse)
async def update_schedule_block(
    schedule_id: UUID,
    block_id: str,
    data: ScheduleBlockUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ScheduleService(db)
    return await service.update_block(current_user.id, schedule_id, block_id, data)


@router.delete("/{schedule_id}/blocks/{block_id}", response_model=ScheduleResponse)
async def delete_schedule_block(
    schedule_id: UUID,
    block_id: str,
    current_user: CurrentUser,
    db: DbSession,
):
    service = ScheduleService(db)
    return await service.delete_block(current_user.id, schedule_id, block_id)


# ─── AI-powered schedule generation ────────────────────────────────────


@router.post("/generate", response_model=ScheduleResponse)
async def generate_schedule(
    data: ScheduleGenerateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    engine = SchedulingEngine(db)
    return await engine.generate(current_user, data)


@router.post("/generate/multi-day", response_model=list[ScheduleResponse])
async def generate_multi_day_schedule(
    data: ScheduleGenerateMultiRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    engine = SchedulingEngine(db)
    return await engine.generate_multi_day(current_user, data)


@router.post("/regenerate", response_model=ScheduleResponse)
async def regenerate_schedule(
    data: ScheduleRegenerateRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    engine = SchedulingEngine(db)
    return await engine.regenerate(current_user, data)


@router.get("/today/current", response_model=ScheduleResponse)
async def get_today_schedule(current_user: CurrentUser, db: DbSession):
    engine = SchedulingEngine(db)
    schedule = await engine.get_today(current_user.id)
    if not schedule:
        raise HTTPException(status_code=404, detail="No schedule found for today")
    return schedule


@router.get("/week/current", response_model=list[ScheduleResponse])
async def get_week_schedule(
    current_user: CurrentUser,
    db: DbSession,
    start: date | None = None,
):
    engine = SchedulingEngine(db)
    return await engine.get_week(current_user.id, start)
