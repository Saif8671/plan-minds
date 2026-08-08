import uuid
from datetime import time

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
            fixed_end=time(16, 0),
            duration=420,
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

    from datetime import date

    result = engine._build_schedule(tasks, date.today(), time(6, 0), time(23, 0))

    assert isinstance(result, GeneratedSchedule)
    assert len(result.blocks) >= 2
    fixed = [b for b in result.blocks if b.is_fixed]
    assert len(fixed) >= 1
    college_block = next((b for b in fixed if b.title == "College"), None)
    assert college_block is not None
    assert college_block.start == time(9, 0)



def test_has_conflict():
    engine = SchedulingEngine(db=None)  # type: ignore
    blocks = [
        ScheduleBlock(title="A", start=time(9, 0), end=time(10, 0), is_fixed=True),
    ]
    assert engine._has_conflict(time(9, 30), time(10, 30), blocks) is True
    assert engine._has_conflict(time(10, 0), time(11, 0), blocks) is False
