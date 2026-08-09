from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.models import TaskStatus
from app.schemas.auth import PaginatedResponse
from app.schemas.task import TaskActivityCreate, TaskCreate, TaskResponse, TaskUpdate
from app.services.tasks.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, current_user: CurrentUser, db: DbSession):
    service = TaskService(db)
    return await service.create_task(current_user.id, data)


@router.get("", response_model=PaginatedResponse[TaskResponse])
async def list_tasks(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: TaskStatus | None = None,
):
    service = TaskService(db)
    skip = (page - 1) * page_size
    tasks, total = await service.get_tasks(current_user.id, skip, page_size, status)
    return PaginatedResponse(items=tasks, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, current_user: CurrentUser, db: DbSession):
    service = TaskService(db)
    return await service.get_task(current_user.id, task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = TaskService(db)
    return await service.update_task(current_user.id, task_id, data)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    service = TaskService(db)
    return await service.complete_task(current_user.id, task_id)


@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: UUID, current_user: CurrentUser, db: DbSession):
    service = TaskService(db)
    await service.delete_task(current_user.id, task_id)


@router.post("/{task_id}/activity", status_code=201)
async def log_task_activity(
    task_id: UUID,
    data: TaskActivityCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = TaskService(db)
    return await service.log_activity(current_user.id, task_id, data.time_spent)
