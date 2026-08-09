"""Task API endpoints.

All endpoints require Bearer token authentication.
"""

from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.models import TaskStatus
from app.schemas.base import ApiResponse, PaginatedData, MessageData
from app.schemas.task import (
    TaskActivityCreate,
    TaskCreate,
    TaskResponse,
    TaskSkipRequest,
    TaskUpdate,
)
from app.services.tasks.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

_common_responses = {
    401: {"description": "Not authenticated"},
    404: {"description": "Task not found"},
}


@router.post(
    "",
    response_model=ApiResponse[TaskResponse],
    status_code=201,
    responses={401: {"description": "Not authenticated"}, 422: {"description": "Validation error"}},
    summary="Create a task",
)
async def create_task(data: TaskCreate, current_user: CurrentUser, db: DbSession):
    """Create a new task for the authenticated user.

    Fixed tasks require both `fixed_start` and `fixed_end`.
    If `reminder_time` is provided, a reminder is automatically created.
    """
    service = TaskService(db)
    result = await service.create_task(current_user.id, data)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=ApiResponse[PaginatedData[TaskResponse]],
    responses={401: {"description": "Not authenticated"}},
    summary="List tasks",
)
async def list_tasks(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    status: TaskStatus | None = Query(None, description="Filter by status"),
):
    """Return a paginated list of the user's tasks, optionally filtered by status."""
    service = TaskService(db)
    skip = (page - 1) * page_size
    tasks, total = await service.get_tasks(current_user.id, skip, page_size, status)
    return ApiResponse(data=PaginatedData(items=tasks, total=total, page=page, page_size=page_size))


@router.get(
    "/{task_id}",
    response_model=ApiResponse[TaskResponse],
    responses=_common_responses,
    summary="Get a task",
)
async def get_task(task_id: UUID, current_user: CurrentUser, db: DbSession):
    """Return a single task by ID."""
    service = TaskService(db)
    result = await service.get_task(current_user.id, task_id)
    return ApiResponse(data=result)


@router.patch(
    "/{task_id}",
    response_model=ApiResponse[TaskResponse],
    responses=_common_responses,
    summary="Update a task",
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Partially update a task. Only provided fields are changed."""
    service = TaskService(db)
    result = await service.update_task(current_user.id, task_id, data)
    return ApiResponse(data=result)


@router.post(
    "/{task_id}/start",
    response_model=ApiResponse[TaskResponse],
    responses=_common_responses,
    summary="Start a task",
)
async def start_task(task_id: UUID, current_user: CurrentUser, db: DbSession):
    """Mark a task as IN_PROGRESS and open an activity log entry with `started_at = now`.

    Use this before `complete` to enable accurate time-spent tracking.
    """
    service = TaskService(db)
    result = await service.start_task(current_user.id, task_id)
    return ApiResponse(data=result)


@router.patch(
    "/{task_id}/complete",
    response_model=ApiResponse[TaskResponse],
    responses=_common_responses,
    summary="Complete a task",
)
async def complete_task(task_id: UUID, current_user: CurrentUser, db: DbSession):
    """Mark a task as COMPLETED.

    - Records actual time spent (computed from `start_task` timestamp if called prior)
    - Awards XP based on priority and duration
    - Spawns the next recurring instance if the task is recurring
    """
    service = TaskService(db)
    result = await service.complete_task(current_user.id, task_id)
    return ApiResponse(data=result)


@router.post(
    "/{task_id}/skip",
    response_model=ApiResponse[TaskResponse],
    responses=_common_responses,
    summary="Skip a task",
)
async def skip_task(
    task_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
    data: TaskSkipRequest | None = None,
):
    """Mark a task as SKIPPED with an optional reason.

    The skip is recorded in the activity log for habit learning analytics.
    """
    service = TaskService(db)
    reason = data.reason if data else None
    result = await service.skip_task(current_user.id, task_id, reason)
    return ApiResponse(data=result)


@router.delete(
    "/{task_id}",
    status_code=204,
    responses=_common_responses,
    summary="Delete a task",
)
async def delete_task(task_id: UUID, current_user: CurrentUser, db: DbSession):
    """Permanently delete a task and all its reminders and activity logs."""
    service = TaskService(db)
    await service.delete_task(current_user.id, task_id)


@router.post(
    "/{task_id}/activity",
    status_code=201,
    response_model=ApiResponse[MessageData],
    responses=_common_responses,
    summary="Log task activity",
)
async def log_task_activity(
    task_id: UUID,
    data: TaskActivityCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    """Manually log time spent on a task (in minutes)."""
    service = TaskService(db)
    result = await service.log_activity(current_user.id, task_id, data.time_spent)
    return ApiResponse(data=MessageData(message=result["message"]))
