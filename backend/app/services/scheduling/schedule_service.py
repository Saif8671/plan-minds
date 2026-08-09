"""Schedule service — CRUD + block editing operations.

Block operations all pass through ScheduleValidator before persisting,
so any change that would create a conflict is caught immediately.
"""

from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ScheduleConflictError, ValidationError
from app.models import Schedule, ScheduleStatus
from app.repositories.schedule_repository import ScheduleRepository
from app.schemas.schedule import (
    GeneratedSchedule,
    ScheduleBlock,
    ScheduleBlockCreate,
    ScheduleBlockMove,
    ScheduleBlockUpdate,
    ScheduleCreate,
    ScheduleMergeRequest,
    ScheduleResponse,
    ScheduleSplitRequest,
    ScheduleUpdate,
    ValidationResultResponse,
)
from app.services.scheduling.conflict_resolution import ConflictResolutionService
from app.services.scheduling.validator import ScheduleValidator


class ScheduleService:
    def __init__(self, db: AsyncSession):
        self.schedule_repo = ScheduleRepository(db)

    # ─── CRUD ─────────────────────────────────────────────────────────

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

        if "start_time" in update_data and update_data["start_time"]:
            schedule.date = update_data["start_time"].date()

        schedule = await self.schedule_repo.update(schedule)
        return ScheduleResponse.model_validate(schedule)

    async def delete_schedule(self, user_id: UUID, schedule_id: UUID) -> None:
        schedule = await self.schedule_repo.get_by_id_and_user(schedule_id, user_id)
        if not schedule:
            raise NotFoundError("Schedule")
        await self.schedule_repo.delete(schedule)

    # ─── Block CRUD ───────────────────────────────────────────────────

    async def create_block(
        self, user_id: UUID, schedule_id: UUID, data: ScheduleBlockCreate
    ) -> ScheduleResponse:
        """Add a new block to an existing generated schedule."""
        schedule, generated = await self._load_generated(user_id, schedule_id)
        new_block = ScheduleBlock(
            id=uuid4().hex,
            title=data.title,
            start=data.start,
            end=data.end,
            category=data.category,
            is_fixed=data.is_fixed,
            task_id=data.task_id,
        )
        generated.blocks.append(new_block)
        return await self._save_validated(schedule, generated)

    async def update_block(
        self, user_id: UUID, schedule_id: UUID, block_id: str, data: ScheduleBlockUpdate
    ) -> ScheduleResponse:
        """Update an existing block's fields."""
        schedule, generated = await self._load_generated(user_id, schedule_id)
        block = self._find_block(generated, block_id)

        if data.title is not None:
            block.title = data.title
        if data.start is not None:
            block.start = data.start
        if data.end is not None:
            block.end = data.end
        if data.category is not None:
            block.category = data.category

        return await self._save_validated(schedule, generated)

    async def move_block(
        self, user_id: UUID, schedule_id: UUID, block_id: str, data: ScheduleBlockMove
    ) -> ScheduleResponse:
        """Move a block to a new time window."""
        schedule, generated = await self._load_generated(user_id, schedule_id)
        block = self._find_block(generated, block_id)
        block.start = data.new_start
        block.end = data.new_end
        return await self._save_validated(schedule, generated)

    async def delete_block(
        self, user_id: UUID, schedule_id: UUID, block_id: str
    ) -> ScheduleResponse:
        """Remove a block from the schedule."""
        schedule, generated = await self._load_generated(user_id, schedule_id)
        original_count = len(generated.blocks)
        generated.blocks = [b for b in generated.blocks if b.id != block_id]
        if len(generated.blocks) == original_count:
            raise NotFoundError("ScheduleBlock")
        return await self._save_validated(schedule, generated)

    async def split_block(
        self, user_id: UUID, schedule_id: UUID, block_id: str, data: ScheduleSplitRequest
    ) -> ScheduleResponse:
        """Split a block at a given time, creating two contiguous blocks."""
        schedule, generated = await self._load_generated(user_id, schedule_id)
        block = self._find_block(generated, block_id)

        split_at = data.split_at
        if not (block.start < split_at < block.end):
            raise ValidationError(
                f"split_at ({split_at}) must be strictly between block start ({block.start}) and end ({block.end})"
            )

        first = ScheduleBlock(
            id=uuid4().hex,
            title=block.title + " (1/2)",
            start=block.start,
            end=split_at,
            category=block.category,
            is_fixed=block.is_fixed,
            task_id=block.task_id,
        )
        second = ScheduleBlock(
            id=uuid4().hex,
            title=block.title + " (2/2)",
            start=split_at,
            end=block.end,
            category=block.category,
            is_fixed=False,
            task_id=None,
        )
        generated.blocks = [b for b in generated.blocks if b.id != block_id]
        generated.blocks.extend([first, second])
        return await self._save_validated(schedule, generated)

    async def merge_blocks(
        self, user_id: UUID, schedule_id: UUID, data: ScheduleMergeRequest
    ) -> ScheduleResponse:
        """Merge two adjacent blocks into one spanning their combined time."""
        if len(data.block_ids) != 2:
            raise ValidationError("Exactly 2 block_ids are required for merge")

        schedule, generated = await self._load_generated(user_id, schedule_id)
        blocks_to_merge = [self._find_block(generated, bid) for bid in data.block_ids]
        blocks_to_merge.sort(key=lambda b: b.start)
        a, b = blocks_to_merge

        if a.end != b.start:
            raise ValidationError(
                f"Blocks must be adjacent to merge. Gap: {a.end} → {b.start}"
            )

        merged = ScheduleBlock(
            id=uuid4().hex,
            title=data.merged_title or f"{a.title} + {b.title}",
            start=a.start,
            end=b.end,
            category=a.category,
            is_fixed=a.is_fixed and b.is_fixed,
            task_id=a.task_id,
        )
        ids_to_remove = {a.id, b.id}
        generated.blocks = [bl for bl in generated.blocks if bl.id not in ids_to_remove]
        generated.blocks.append(merged)
        return await self._save_validated(schedule, generated)

    # ─── Validation endpoint helper ───────────────────────────────────

    async def validate_schedule(
        self, user_id: UUID, schedule_id: UUID, buffer_minutes: int = 5
    ) -> ValidationResultResponse:
        """Run all validation rules on an existing schedule and return the result."""
        schedule, generated = await self._load_generated(user_id, schedule_id)
        result = ScheduleValidator.validate(generated, buffer_minutes=buffer_minutes)
        return ValidationResultResponse(**result.to_dict())

    # ─── Private helpers ──────────────────────────────────────────────

    async def _load_generated(
        self, user_id: UUID, schedule_id: UUID
    ) -> tuple[Schedule, GeneratedSchedule]:
        schedule = await self.schedule_repo.get_by_id_and_user(schedule_id, user_id)
        if not schedule or not schedule.generated_schedule:
            raise NotFoundError("Schedule or GeneratedSchedule")
        generated = GeneratedSchedule.model_validate(schedule.generated_schedule)
        return schedule, generated

    def _find_block(self, generated: GeneratedSchedule, block_id: str) -> ScheduleBlock:
        for block in generated.blocks:
            if block.id == block_id:
                return block
        raise NotFoundError("ScheduleBlock")

    async def _save_validated(
        self, schedule: Schedule, generated: GeneratedSchedule
    ) -> ScheduleResponse:
        """Sort blocks, run validator, raise on errors, persist, return response."""
        generated.blocks.sort(key=lambda b: b.start)

        # Run legacy suggestions (ConflictResolutionService) + new validator
        generated.suggestions = ConflictResolutionService.analyze_schedule(generated)
        result = ScheduleValidator.validate(generated)

        if not result.is_valid:
            raise ScheduleConflictError(
                conflicts=[c.to_dict() for c in result.conflicts if c.severity == "error"]
            )

        schedule.generated_schedule = generated.model_dump(mode="json")
        schedule = await self.schedule_repo.update(schedule)
        return ScheduleResponse.model_validate(schedule)
