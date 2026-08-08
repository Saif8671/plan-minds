"""Background scheduler for reminders and missed task detection.

Uses APScheduler to run periodic jobs:
- check_upcoming_reminders: fires every 60s, finds unsent reminders due now
- check_missed_tasks: fires every 5 min, detects tasks past their deadline
"""

from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import AsyncSessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


async def check_upcoming_reminders() -> None:
    """Find unsent reminders whose time has arrived and create notifications."""
    # Lazy imports to avoid circular dependencies at module level
    from sqlalchemy import and_, select

    from app.models import Notification, NotificationType, Reminder

    async with AsyncSessionLocal() as session:
        try:
            now = datetime.now(UTC)
            result = await session.execute(
                select(Reminder).where(
                    and_(
                        Reminder.is_sent.is_(False),
                        Reminder.reminder_time <= now,
                    )
                )
            )
            reminders = list(result.scalars().all())

            for reminder in reminders:
                # Create in-app notification
                notification = Notification(
                    user_id=reminder.user_id,
                    title=reminder.title,
                    message=reminder.message or f"Reminder: {reminder.title}",
                    notification_type=NotificationType.TASK_REMINDER,
                    data={
                        "reminder_id": str(reminder.id),
                        "task_id": str(reminder.task_id) if reminder.task_id else None,
                    },
                )
                session.add(notification)

                # Try Web Push (non-blocking)
                try:
                    from app.services.notifications.push_service import PushService

                    push_service = PushService(session)
                    await push_service.send_push_notification(
                        user_id=reminder.user_id,
                        title=reminder.title,
                        body=reminder.message or f"Reminder: {reminder.title}",
                        data={"reminder_id": str(reminder.id)},
                    )
                except Exception:
                    logger.debug("Push notification skipped (no VAPID key or no subs)")

                # Mark reminder as sent
                reminder.is_sent = True

            if reminders:
                await session.commit()
                logger.info("Processed %d reminders", len(reminders))
        except Exception:
            await session.rollback()
            logger.exception("Error checking reminders")


async def check_missed_tasks() -> None:
    """Detect tasks past their deadline that are still pending."""
    from sqlalchemy import and_, select

    from app.models import Notification, NotificationType, Task, TaskStatus

    async with AsyncSessionLocal() as session:
        try:
            now = datetime.now(UTC)
            result = await session.execute(
                select(Task).where(
                    and_(
                        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
                        Task.deadline.isnot(None),
                        Task.deadline < now,
                    )
                )
            )
            missed_tasks = list(result.scalars().all())

            for task in missed_tasks:
                notification = Notification(
                    user_id=task.user_id,
                    title=f"Missed: {task.title}",
                    message=f"Your task '{task.title}' has passed its deadline.",
                    notification_type=NotificationType.TASK_MISSED,
                    data={"task_id": str(task.id)},
                )
                session.add(notification)

                # Try Web Push (non-blocking)
                try:
                    from app.services.notifications.push_service import PushService

                    push_service = PushService(session)
                    await push_service.send_push_notification(
                        user_id=task.user_id,
                        title=f"Missed: {task.title}",
                        body=f"Your task '{task.title}' has passed its deadline.",
                        data={"task_id": str(task.id)},
                    )
                except Exception:
                    logger.debug("Push notification skipped")

                task.status = TaskStatus.SKIPPED

            if missed_tasks:
                await session.commit()
                logger.info("Detected %d missed tasks", len(missed_tasks))
        except Exception:
            await session.rollback()
            logger.exception("Error checking missed tasks")


def start_scheduler() -> None:
    """Start the background scheduler with reminder and missed-task jobs."""
    scheduler.add_job(
        check_upcoming_reminders,
        "interval",
        seconds=60,
        id="check_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        check_missed_tasks,
        "interval",
        minutes=5,
        id="check_missed_tasks",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Background scheduler stopped")
