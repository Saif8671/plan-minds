from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.task_repo = TaskRepository(db)

    async def create_task(self, user_id: UUID, data: TaskCreate) -> TaskResponse:
        if data.is_fixed and (not data.fixed_start or not data.fixed_end):
            raise ValidationError("Fixed tasks require fixed_start and fixed_end")

        task = Task(user_id=user_id, **data.model_dump())
        task = await self.task_repo.create(task)
        return TaskResponse.model_validate(task)

    async def get_tasks(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status=None,
    ) -> tuple[list[TaskResponse], int]:
        tasks = await self.task_repo.get_by_user(user_id, skip, limit, status)
        total = await self.task_repo.count_by_user(user_id, status)
        return [TaskResponse.model_validate(t) for t in tasks], total

    async def get_task(self, user_id: UUID, task_id: UUID) -> TaskResponse:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        return TaskResponse.model_validate(task)

    async def update_task(
        self, user_id: UUID, task_id: UUID, data: TaskUpdate
    ) -> TaskResponse:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task = await self.task_repo.update(task)
        return TaskResponse.model_validate(task)

    async def delete_task(self, user_id: UUID, task_id: UUID) -> None:
        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            raise NotFoundError("Task")
        await self.task_repo.delete(task)
