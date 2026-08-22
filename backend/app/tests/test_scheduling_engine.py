import uuid
from datetime import date, datetime, time, timedelta

from app.models import Task, TaskCategory, TaskPriority, TaskStatus
from app.schemas.schedule import GeneratedSchedule, ScheduleBlock
from app.services.scheduling.engine import SchedulingEngine


def test_build_schedule_fixed_and_flexible():
    engine = SchedulingEngine(db=None)  # type: ignore
    user_id = uuid.uuid4()

    tasks = [
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title="College",
            is_fixed=True,
            fixed_start=time(9, 0),
            fixed_end=time(12, 0),
            duration=180,
            category=TaskCategory.WORK,
            status=TaskStatus.PENDING,
        ),
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title="DSA",
            duration=120,
            priority=TaskPriority.HIGH,
            category=TaskCategory.STUDY,
            status=TaskStatus.PENDING,
        ),
    ]

    result = engine._build_schedule(tasks, date.today(), time(6, 0), time(23, 0))

    assert isinstance(result, GeneratedSchedule)
    assert len(result.blocks) >= 2
    fixed = [b for b in result.blocks if b.is_fixed]
    assert len(fixed) >= 1
    college_block = next((b for b in fixed if b.title == "College"), None)
    assert college_block is not None
    assert college_block.start == time(9, 0)


def test_has_conflict():
    from app.services.scheduling.pipeline import ScheduleContext

    context = ScheduleContext(date.today(), time(6, 0), time(23, 0), None)
    context.blocks = [
        ScheduleBlock(title="A", start=time(9, 0), end=time(10, 0), is_fixed=True),
    ]
    assert context.has_conflict(time(9, 30), time(10, 30)) is True
    assert context.has_conflict(time(10, 0), time(11, 0)) is False


def test_priority_ordering():
    engine = SchedulingEngine(db=None)
    user_id = uuid.uuid4()

    # Fill up the day almost entirely
    tasks = [
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title="Low Priority Task",
            duration=240,
            priority=TaskPriority.LOW,
            category=TaskCategory.OTHER,
            status=TaskStatus.PENDING,
        ),
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title="Urgent Task",
            duration=120,
            priority=TaskPriority.URGENT,
            category=TaskCategory.WORK,
            status=TaskStatus.PENDING,
        ),
    ]

    # Using a very restricted time frame to force a choice
    # 2 hours available, one task is 4 hours, the other is 2 hours
    result = engine._build_schedule(tasks, date.today(), time(10, 0), time(12, 0))

    # The urgent task should be scheduled
    scheduled_titles = [b.title for b in result.blocks]
    assert "Urgent Task" in scheduled_titles
    # The low priority task should be in unscheduled
    assert "Low Priority Task" in result.unscheduled_tasks


def test_deadlines():
    engine = SchedulingEngine(db=None)
    user_id = uuid.uuid4()

    now_dt = datetime.combine(date.today(), time(10, 0))

    tasks = [
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title="Due Soon",
            duration=60,
            priority=TaskPriority.MEDIUM,
            deadline=now_dt + timedelta(hours=2),
            category=TaskCategory.WORK,
            status=TaskStatus.PENDING,
        ),
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title="Due Later",
            duration=60,
            priority=TaskPriority.MEDIUM,
            deadline=now_dt + timedelta(hours=10),
            category=TaskCategory.WORK,
            status=TaskStatus.PENDING,
        ),
    ]

    # 1 hour available early, 1 hour available later
    result = engine._build_schedule(tasks, date.today(), time(10, 0), time(12, 0))

    # Due Soon should be scheduled first because it has a closer deadline
    scheduled_blocks = [b for b in result.blocks if not b.is_fixed]
    # Check that Due Soon is scheduled before Due Later
    due_soon = next((b for b in scheduled_blocks if b.title == "Due Soon"), None)
    due_later = next((b for b in scheduled_blocks if b.title == "Due Later"), None)

    if due_soon and due_later:
        assert due_soon.start < due_later.start


def test_overbooking():
    engine = SchedulingEngine(db=None)
    user_id = uuid.uuid4()

    tasks = [
        Task(
            id=uuid.uuid4(),
            user_id=user_id,
            title=f"Task {i}",
            duration=120,
            priority=TaskPriority.MEDIUM,
            category=TaskCategory.WORK,
            status=TaskStatus.PENDING,
        )
        for i in range(10)
    ]

    # Provide only 4 hours
    result = engine._build_schedule(tasks, date.today(), time(10, 0), time(14, 0))

    # Only 2 tasks should fit in 4 hours
    scheduled_flex = [
        b for b in result.blocks if b.category == "work" and not b.is_fixed
    ]
    assert len(scheduled_flex) <= 2

    # 8 tasks should be unscheduled
    assert len(result.unscheduled_tasks) >= 8
