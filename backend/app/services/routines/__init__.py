from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Routine
from app.repositories.routine_repository import RoutineRepository
from app.schemas.routine import RoutineCreate, RoutineResponse, RoutineUpdate


class RoutineService:
    def __init__(self, db: AsyncSession):
        self.routine_repo = RoutineRepository(db)

    async def create_routine(
        self, user_id: UUID, data: RoutineCreate
    ) -> RoutineResponse:
        routine = Routine(user_id=user_id, **data.model_dump())
        routine = await self.routine_repo.create(routine)
        return RoutineResponse.model_validate(routine)

    async def get_routines(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> tuple[list[RoutineResponse], int]:
        routines = await self.routine_repo.get_by_user(
            user_id, skip, limit, active_only
        )
        total = await self.routine_repo.count_by_user(user_id, active_only)
        return [RoutineResponse.model_validate(r) for r in routines], total

    async def get_routine(self, user_id: UUID, routine_id: UUID) -> RoutineResponse:
        routine = await self.routine_repo.get_by_id_and_user(routine_id, user_id)
        if not routine:
            raise NotFoundError("Routine")
        return RoutineResponse.model_validate(routine)

    async def update_routine(
        self, user_id: UUID, routine_id: UUID, data: RoutineUpdate
    ) -> RoutineResponse:
        routine = await self.routine_repo.get_by_id_and_user(routine_id, user_id)
        if not routine:
            raise NotFoundError("Routine")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(routine, field, value)

        routine = await self.routine_repo.update(routine)
        return RoutineResponse.model_validate(routine)

    async def delete_routine(self, user_id: UUID, routine_id: UUID) -> None:
        routine = await self.routine_repo.get_by_id_and_user(routine_id, user_id)
        if not routine:
            raise NotFoundError("Routine")
        await self.routine_repo.delete(routine)
