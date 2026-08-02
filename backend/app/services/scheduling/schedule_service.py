from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Schedule, ScheduleStatus
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ScheduleUpdate


class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.schedule_repo = ScheduleRepository(db)

    async def create_schedule(
        self, user_id: UUID, data: ScheduleCreate
    ) -> ScheduleResponse:
        schedule = Schedule(
            user_id=user_id,
            title=data.title,
            description=data.description,
            priority=data.priority,
            start_time=data.start_time,
            end_time=data.end_time,
            status=data.status,
            category=data.category,
            date=data.start_time.date(),
        )
        schedule = await self.schedule_repo.create(schedule)
        return ScheduleResponse.model_validate(schedule)

    async def get_schedules(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: ScheduleStatus | None = None,
    ) -> tuple[list[ScheduleResponse], int]:
        schedules = await self.schedule_repo.get_by_user(user_id, skip, limit, status)
        total = await self.schedule_repo.count_by_user(user_id, status)
        return [ScheduleResponse.model_validate(s) for s in schedules], total

    async def get_schedule(self, user_id: UUID, schedule_id: UUID) -> ScheduleResponse:
        schedule = await self.schedule_repo.get_by_id_and_user(schedule_id, user_id)
        if not schedule:
            raise NotFoundError("Schedule")
        return ScheduleResponse.model_validate(schedule)

    async def update_schedule(
        self, user_id: UUID, schedule_id: UUID, data: ScheduleUpdate
    ) -> ScheduleResponse:
        schedule = await self.schedule_repo.get_by_id_and_user(schedule_id, user_id)
        if not schedule:
            raise NotFoundError("Schedule")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        # Update the date field if start_time changes
        if "start_time" in update_data and update_data["start_time"]:
            schedule.date = update_data["start_time"].date()

        schedule = await self.schedule_repo.update(schedule)
        return ScheduleResponse.model_validate(schedule)

    async def delete_schedule(self, user_id: UUID, schedule_id: UUID) -> None:
        schedule = await self.schedule_repo.get_by_id_and_user(schedule_id, user_id)
        if not schedule:
            raise NotFoundError("Schedule")
        await self.schedule_repo.delete(schedule)
