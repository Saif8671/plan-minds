"""Complete reminder service.

Features:
- One-time reminders
- Recurring reminders (daily/weekly/monthly)
- Reminder history tracking (sent/snoozed/dismissed/missed)
- Missed reminder detection
- Auto-generate reminders from schedule blocks
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logger import get_logger
from app.models import (
    Notification,
    NotificationType,
    RecurrenceType,
    Reminder,
    ReminderHistory,
    ReminderOutcome,
    ReminderType,
    Schedule,
)
from app.repositories.reminder_repository import ReminderRepository
from app.schemas.reminder import (
    ReminderCreate,
    ReminderCreateRecurring,
    ReminderHistoryResponse,
    ReminderResponse,
    ReminderUpdate,
)
from app.services.notifications.push_service import PushService

logger = get_logger(__name__)


class ReminderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.reminder_repo = ReminderRepository(db)
        self.push_service = PushService(db)

    # ─── CRUD ─────────────────────────────────────────────────────────

    async def create_reminder(
        self, user_id: UUID, data: ReminderCreate
    ) -> ReminderResponse:
        reminder = Reminder(
            user_id=user_id,
            task_occurrence_id=data.task_id,
            title=data.title,
            reminder_type=data.reminder_type,
            reminder_time=data.reminder_time,
            message=data.message,
        )
        reminder = await self.reminder_repo.create(reminder)
        return ReminderResponse.model_validate(reminder)

    async def create_recurring_reminder(
        self, user_id: UUID, data: ReminderCreateRecurring
    ) -> ReminderResponse:
        """Create a recurring reminder and pre-compute its next fire time."""
        reminder = Reminder(
            user_id=user_id,
            task_occurrence_id=data.task_id,
            title=data.title,
            reminder_type=data.reminder_type,
            reminder_time=data.reminder_time,
            message=data.message,
            recurrence=data.recurrence,
            recurrence_rule=data.recurrence_rule,
            next_fire=data.reminder_time,
        )
        reminder = await self.reminder_repo.create(reminder)
        return ReminderResponse.model_validate(reminder)

    async def get_reminders(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
        include_sent: bool = True,
    ) -> list[ReminderResponse]:
        reminders = await self.reminder_repo.get_by_user(
            user_id, skip, limit, include_sent
        )
        return [ReminderResponse.model_validate(r) for r in reminders]

    async def update_reminder(
        self, user_id: UUID, reminder_id: UUID, data: ReminderUpdate
    ) -> ReminderResponse:
        reminder = await self._get_owned(user_id, reminder_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(reminder, field, value)
        reminder = await self.reminder_repo.update(reminder)
        return ReminderResponse.model_validate(reminder)

    async def delete_reminder(self, user_id: UUID, reminder_id: UUID) -> None:
        reminder = await self._get_owned(user_id, reminder_id)
        await self.reminder_repo.delete(reminder)

    # ─── Actions ──────────────────────────────────────────────────────

    async def snooze_reminder(
        self, user_id: UUID, reminder_id: UUID, snooze_minutes: int = 10
    ) -> ReminderResponse:
        reminder = await self._get_owned(user_id, reminder_id)
        reminder.is_snoozed = True
        reminder.snooze_until = datetime.now(UTC) + timedelta(minutes=snooze_minutes)
        reminder.is_sent = False  # Will re-trigger after snooze_until
        reminder = await self.reminder_repo.update(reminder)

        await self._record_history(reminder.id, datetime.now(UTC), ReminderOutcome.SNOOZED)
        return ReminderResponse.model_validate(reminder)

    async def complete_reminder(
        self, user_id: UUID, reminder_id: UUID
    ) -> ReminderResponse:
        reminder = await self._get_owned(user_id, reminder_id)
        reminder.is_completed = True
        reminder.is_sent = True
        reminder = await self.reminder_repo.update(reminder)

        await self._record_history(reminder.id, datetime.now(UTC), ReminderOutcome.DISMISSED)
        return ReminderResponse.model_validate(reminder)

    # ─── History ──────────────────────────────────────────────────────

    async def get_reminder_history(
        self, user_id: UUID, reminder_id: UUID, limit: int = 50
    ) -> list[ReminderHistoryResponse]:
        """Return the fire history for a specific reminder."""
        reminder = await self._get_owned(user_id, reminder_id)
        result = await self.db.execute(
            select(ReminderHistory)
            .where(ReminderHistory.reminder_id == reminder.id)
            .order_by(ReminderHistory.fired_at.desc())
            .limit(limit)
        )
        history = result.scalars().all()
        return [ReminderHistoryResponse.model_validate(h) for h in history]

    # ─── Worker-called methods ─────────────────────────────────────────

    async def process_fired_reminder(self, reminder: Reminder) -> None:
        """Called by the background worker when a reminder is due.

        - Sends push notification
        - Logs to ReminderHistory
        - Advances next_fire for recurring reminders
        """
        now = datetime.now(UTC)

        # Send push notification
        try:
            await self.push_service.send_push_notification(
                user_id=reminder.user_id,
                title=reminder.title,
                body=reminder.message or "You have a reminder!",
                data={"reminder_id": str(reminder.id)},
            )
        except Exception as exc:
            logger.warning("Push notification failed for reminder %s: %s", reminder.id, exc)

        # Create in-app notification
        notification = Notification(
            user_id=reminder.user_id,
            title=reminder.title,
            message=reminder.message or "Reminder",
            notification_type=NotificationType.TASK_REMINDER,
            data={"reminder_id": str(reminder.id)},
        )
        self.db.add(notification)

        # Log outcome
        await self._record_history(reminder.id, now, ReminderOutcome.SENT)

        # Handle recurring: advance next_fire
        if reminder.recurrence:
            reminder.next_fire = self._compute_next_fire(
                now, reminder.recurrence, reminder.recurrence_rule
            )
            reminder.is_sent = False  # Will fire again
        else:
            reminder.is_sent = True

        reminder.is_snoozed = False
        reminder.snooze_until = None
        await self.reminder_repo.update(reminder)

    async def detect_missed_reminders(self, window_minutes: int = 15) -> int:
        """Find reminders that fired but were never sent (process_fired not called).

        Returns the count of newly-marked-missed reminders.
        """
        cutoff = datetime.now(UTC) - timedelta(minutes=window_minutes)
        result = await self.db.execute(
            select(Reminder).where(
                Reminder.is_sent == False,  # noqa: E712
                Reminder.is_snoozed == False,  # noqa: E712
                Reminder.is_completed == False,  # noqa: E712
                Reminder.reminder_time <= cutoff,
            )
        )
        missed = result.scalars().all()
        count = 0
        for reminder in missed:
            await self._record_history(reminder.id, reminder.reminder_time, ReminderOutcome.MISSED)
            reminder.is_sent = True  # Mark as processed so we don't detect it again
            await self.reminder_repo.update(reminder)
            count += 1

        if count:
            logger.info("Marked %d reminders as missed", count)
        return count

    async def generate_schedule_reminders(self, schedule_id: UUID) -> int:
        """Auto-create reminders for each block in a generated schedule.

        Returns number of reminders created.
        """
        from datetime import date, time

        result = await self.db.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()
        if not schedule or not schedule.generated_schedule:
            raise NotFoundError("Schedule or GeneratedSchedule")

        created = 0
        blocks = schedule.generated_schedule.get("blocks", [])
        schedule_date = schedule.date or date.today()

        for block in blocks:
            block_start_str = block.get("start")
            if not block_start_str:
                continue
            try:
                t = time.fromisoformat(block_start_str)
                fire_dt = datetime.combine(schedule_date, t).replace(tzinfo=UTC)
                # Set reminder 10 min before block start
                reminder_time = fire_dt - timedelta(minutes=10)
                if reminder_time <= datetime.now(UTC):
                    continue
                reminder = Reminder(
                    user_id=schedule.user_id,
                    title=f"Starting soon: {block.get('title', 'Task')}",
                    reminder_type=ReminderType.TASK,
                    reminder_time=reminder_time,
                    message=f"Your task '{block.get('title')}' starts at {block_start_str}",
                )
                self.db.add(reminder)
                created += 1
            except (ValueError, TypeError):
                continue

        await self.db.flush()
        return created

    # ─── Private helpers ──────────────────────────────────────────────

    async def _get_owned(self, user_id: UUID, reminder_id: UUID) -> Reminder:
        result = await self.db.execute(
            select(Reminder).where(
                Reminder.id == reminder_id,
                Reminder.user_id == user_id,
            )
        )
        reminder = result.scalar_one_or_none()
        if not reminder:
            raise NotFoundError("Reminder")
        return reminder

    async def _record_history(
        self, reminder_id: UUID, fired_at: datetime, outcome: ReminderOutcome, notes: str | None = None
    ) -> None:
        history = ReminderHistory(
            reminder_id=reminder_id,
            fired_at=fired_at,
            outcome=outcome,
            notes=notes,
        )
        self.db.add(history)
        await self.db.flush()

    @staticmethod
    def _compute_next_fire(
        after: datetime,
        recurrence: RecurrenceType,
        rule: dict | None,
    ) -> datetime:
        interval = 1
        if rule:
            interval = rule.get("interval", 1)

        if recurrence == RecurrenceType.DAILY:
            return after + timedelta(days=interval)
        elif recurrence == RecurrenceType.WEEKLY:
            return after + timedelta(weeks=interval)
        elif recurrence == RecurrenceType.MONTHLY:
            # Approximate: add 30 * interval days
            return after + timedelta(days=30 * interval)
        else:
            return after + timedelta(days=1)
