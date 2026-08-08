from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import PaginatedResponse
from app.schemas.routine import RoutineCreate, RoutineResponse, RoutineUpdate
from app.services.routines import RoutineService

router = APIRouter(prefix="/routines", tags=["Routines"])


@router.post("", response_model=RoutineResponse, status_code=201)
async def create_routine(
    data: RoutineCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = RoutineService(db)
    return await service.create_routine(current_user.id, data)


@router.get("", response_model=PaginatedResponse[RoutineResponse])
async def list_routines(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    active_only: bool = False,
):
    service = RoutineService(db)
    skip = (page - 1) * page_size
    routines, total = await service.get_routines(
        current_user.id, skip, page_size, active_only
    )
    return PaginatedResponse(
        items=routines, total=total, page=page, page_size=page_size
    )


@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(
    routine_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = RoutineService(db)
    return await service.get_routine(current_user.id, routine_id)


@router.patch("/{routine_id}", response_model=RoutineResponse)
async def update_routine(
    routine_id: UUID,
    data: RoutineUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = RoutineService(db)
    return await service.update_routine(current_user.id, routine_id, data)


@router.delete("/{routine_id}", status_code=204)
async def delete_routine(
    routine_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = RoutineService(db)
    await service.delete_routine(current_user.id, routine_id)
