import uuid
from datetime import date, datetime, time, timedelta

from app.models import RecurrenceType, Task, TaskCategory, TaskPriority, TaskStatus
from app.schemas.schedule import GeneratedSchedule
from app.services.ai.suggestion_service import AISuggestionService
from app.services.scheduling.engine import SchedulingEngine


def test_recurring_daily_task_is_included_for_target_date():
    engine = SchedulingEngine(db=None)  # type: ignore[arg-type]
    user_id = uuid.uuid4()

    task = Task(
        id=uuid.uuid4(),
        user_id=user_id,
        title="Daily Study",
        duration=60,
        priority=TaskPriority.HIGH,
        category=TaskCategory.STUDY,
        status=TaskStatus.PENDING,
        is_recurring=True,
        recurrence=RecurrenceType.DAILY,
        created_at=datetime.now() - timedelta(days=1),
    )

    result = engine._build_schedule([task], date.today(), time(6, 0), time(23, 0))

    assert isinstance(result, GeneratedSchedule)
    assert any(block.title == "Daily Study" for block in result.blocks)


def test_suggestion_service_flags_skipped_habits():
    service = AISuggestionService()
    tasks = [
        Task(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            title="Gym",
            duration=60,
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.HEALTH,
            status=TaskStatus.SKIPPED,
            created_at=datetime.now() - timedelta(days=1),
        )
    ]

    suggestions = service.generate_suggestions(tasks)

    assert any("Gym" in suggestion for suggestion in suggestions)
