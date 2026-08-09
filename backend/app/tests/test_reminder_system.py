"""Unit tests — reminder system: creation, history, recurring, snooze, missed detection."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models import Reminder, ReminderOutcome, ReminderType, RecurrenceType
from app.services.reminders.reminder_service import ReminderService


def make_reminder(**kwargs) -> Reminder:
    defaults = {
        "id": uuid4(),
        "user_id": uuid4(),
        "task_id": None,
        "title": "Test Reminder",
        "reminder_type": ReminderType.CUSTOM,
        "reminder_time": datetime.now(UTC) - timedelta(minutes=2),
        "is_sent": False,
        "is_snoozed": False,
        "is_completed": False,
        "message": "Test message",
        "recurrence": None,
        "recurrence_rule": None,
        "next_fire": None,
        "snooze_until": None,
    }
    defaults.update(kwargs)
    r = MagicMock(spec=Reminder)
    for k, v in defaults.items():
        setattr(r, k, v)
    return r


@pytest.mark.asyncio
async def test_compute_next_fire_daily():
    now = datetime(2026, 8, 9, 10, 0, tzinfo=UTC)
    result = ReminderService._compute_next_fire(now, RecurrenceType.DAILY, None)
    assert result == datetime(2026, 8, 10, 10, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_compute_next_fire_weekly():
    now = datetime(2026, 8, 9, 10, 0, tzinfo=UTC)
    result = ReminderService._compute_next_fire(now, RecurrenceType.WEEKLY, None)
    assert result == datetime(2026, 8, 16, 10, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_compute_next_fire_with_interval():
    now = datetime(2026, 8, 9, 10, 0, tzinfo=UTC)
    result = ReminderService._compute_next_fire(now, RecurrenceType.DAILY, {"interval": 3})
    assert result == datetime(2026, 8, 12, 10, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_process_fired_reminder_one_time():
    """One-time reminder: is_sent should be True after processing."""
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=lambda: []))))
    db.add = MagicMock()
    db.flush = AsyncMock()

    service = ReminderService(db)

    # Patch push service
    with patch.object(service.push_service, "send_push_notification", new_callable=AsyncMock):
        with patch.object(service, "_record_history", new_callable=AsyncMock):
            with patch.object(service.reminder_repo, "update", new_callable=AsyncMock) as mock_update:
                reminder = make_reminder(recurrence=None)
                await service.process_fired_reminder(reminder)
                assert reminder.is_sent is True
                assert reminder.is_snoozed is False


@pytest.mark.asyncio
async def test_process_fired_reminder_recurring():
    """Recurring reminder: next_fire should advance, is_sent should be False."""
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=lambda: []))))
    db.add = MagicMock()
    db.flush = AsyncMock()

    service = ReminderService(db)
    now = datetime.now(UTC)

    with patch.object(service.push_service, "send_push_notification", new_callable=AsyncMock):
        with patch.object(service, "_record_history", new_callable=AsyncMock):
            with patch.object(service.reminder_repo, "update", new_callable=AsyncMock):
                reminder = make_reminder(
                    recurrence=RecurrenceType.DAILY,
                    recurrence_rule=None,
                )
                await service.process_fired_reminder(reminder)
                assert reminder.is_sent is False  # Will re-fire
                assert reminder.next_fire is not None
                assert reminder.next_fire > now


@pytest.mark.asyncio
async def test_detect_missed_reminders():
    """Reminders past their window should be marked as missed."""
    db = AsyncMock()
    old_reminder = make_reminder(
        reminder_time=datetime.now(UTC) - timedelta(minutes=30),
        is_sent=False,
        is_snoozed=False,
        is_completed=False,
    )
    result_mock = MagicMock()
    result_mock.scalars.return_value.all.return_value = [old_reminder]
    db.execute = AsyncMock(return_value=result_mock)
    db.flush = AsyncMock()

    service = ReminderService(db)
    with patch.object(service, "_record_history", new_callable=AsyncMock):
        with patch.object(service.reminder_repo, "update", new_callable=AsyncMock):
            count = await service.detect_missed_reminders(window_minutes=15)
            assert count == 1
            assert old_reminder.is_sent is True
