"""APScheduler background jobs for PlanMinds.

Jobs:
- check_upcoming_reminders   — every 60s  — fires due reminders
- check_snoozed_reminders    — every 60s  — re-fires snoozed reminders past snooze_until
- check_missed_reminders     — every 10m  — detects unfired reminders that slipped through
- check_missed_tasks         — every 5m   — marks overdue tasks as SKIPPED
- cleanup_old_history        — daily      — prunes ReminderHistory older than 90 days
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import AsyncSessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)
scheduler = AsyncIOScheduler()


def start_scheduler() -> None:
    scheduler.add_job(
        check_upcoming_reminders,
        trigger=IntervalTrigger(seconds=60),
        id="check_upcoming_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        check_snoozed_reminders,
        trigger=IntervalTrigger(seconds=60),
        id="check_snoozed_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        check_missed_reminders,
        trigger=IntervalTrigger(minutes=10),
        id="check_missed_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        check_missed_tasks,
        trigger=IntervalTrigger(minutes=5),
        id="check_missed_tasks",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_old_history,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_old_history",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Scheduler started with jobs: %s",
        [job.id for job in scheduler.get_jobs()],
    )


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


# ─── Job implementations ─────────────────────────────────────────────


async def check_upcoming_reminders() -> None:
    """Fire all due, unsent, un-snoozed reminders."""
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.models import Reminder
    from app.services.reminders.reminder_service import ReminderService

    now = datetime.now(UTC)
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Reminder).where(
                    Reminder.is_sent == False,  # noqa: E712
                    Reminder.is_completed == False,  # noqa: E712
                    Reminder.is_snoozed == False,  # noqa: E712
                    Reminder.reminder_time <= now,
                )
            )
            reminders = result.scalars().all()

            if not reminders:
                return

            service = ReminderService(db)
            for reminder in reminders:
                try:
                    await service.process_fired_reminder(reminder)
                except Exception as exc:
                    logger.error("Failed to process reminder %s: %s", reminder.id, exc)

            await db.commit()
            logger.info("Fired %d reminders", len(reminders))
        except Exception as exc:
            await db.rollback()
            logger.error("check_upcoming_reminders job failed: %s", exc)


async def check_snoozed_reminders() -> None:
    """Re-fire reminders whose snooze period has expired."""
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.models import Reminder
    from app.services.reminders.reminder_service import ReminderService

    now = datetime.now(UTC)
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Reminder).where(
                    Reminder.is_snoozed == True,  # noqa: E712
                    Reminder.is_completed == False,  # noqa: E712
                    Reminder.snooze_until <= now,
                )
            )
            reminders = result.scalars().all()

            if not reminders:
                return

            service = ReminderService(db)
            for reminder in reminders:
                # Un-snooze and re-process
                reminder.is_snoozed = False
                try:
                    await service.process_fired_reminder(reminder)
                except Exception as exc:
                    logger.error("Failed to re-fire snoozed reminder %s: %s", reminder.id, exc)

            await db.commit()
            logger.info("Re-fired %d snoozed reminders", len(reminders))
        except Exception as exc:
            await db.rollback()
            logger.error("check_snoozed_reminders job failed: %s", exc)


async def check_missed_reminders() -> None:
    """Detect and record reminders that weren't fired within the 15-minute window."""
    from app.services.reminders.reminder_service import ReminderService

    async with AsyncSessionLocal() as db:
        try:
            service = ReminderService(db)
            count = await service.detect_missed_reminders(window_minutes=15)
            await db.commit()
            if count:
                logger.info("Detected and marked %d missed reminders", count)
        except Exception as exc:
            await db.rollback()
            logger.error("check_missed_reminders job failed: %s", exc)


async def check_missed_tasks() -> None:
    """Auto-skip overdue tasks that are past their deadline without completion."""
    from datetime import UTC, datetime

    from sqlalchemy import select

    from app.models import Task, TaskStatus

    now = datetime.now(UTC)
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Task).where(
                    Task.deadline <= now,
                    Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                )
            )
            tasks = result.scalars().all()

            if not tasks:
                return

            for task in tasks:
                task.status = TaskStatus.SKIPPED

            await db.commit()
            logger.info("Auto-skipped %d overdue tasks", len(tasks))
        except Exception as exc:
            await db.rollback()
            logger.error("check_missed_tasks job failed: %s", exc)


async def cleanup_old_history() -> None:
    """Prune ReminderHistory records older than 90 days."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import delete

    from app.models import ReminderHistory

    cutoff = datetime.now(UTC) - timedelta(days=90)
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                delete(ReminderHistory).where(ReminderHistory.fired_at < cutoff)
            )
            await db.commit()
            if result.rowcount:
                logger.info("Cleaned up %d old reminder history records", result.rowcount)
        except Exception as exc:
            await db.rollback()
            logger.error("cleanup_old_history job failed: %s", exc)
