"""Unit tests — schedule validation rules."""

from datetime import time
from uuid import uuid4

import pytest

from app.schemas.schedule import GeneratedSchedule, ScheduleBlock
from app.services.scheduling.validator import ScheduleValidator


def make_block(title: str, start: str, end: str, **kwargs) -> ScheduleBlock:
    return ScheduleBlock(
        id=uuid4().hex,
        title=title,
        start=time.fromisoformat(start),
        end=time.fromisoformat(end),
        **kwargs,
    )


def make_schedule(blocks: list[ScheduleBlock], wake="07:00", sleep="23:00") -> GeneratedSchedule:
    from datetime import date
    return GeneratedSchedule(
        date=date.today(),
        wake_time=time.fromisoformat(wake),
        sleep_time=time.fromisoformat(sleep),
        blocks=blocks,
    )


class TestOverlapDetection:
    def test_no_conflict(self):
        schedule = make_schedule([
            make_block("Study", "09:00", "10:00"),
            make_block("Gym", "10:30", "11:30"),
        ])
        result = ScheduleValidator.validate(schedule)
        assert result.is_valid

    def test_overlap_detected(self):
        schedule = make_schedule([
            make_block("Study", "09:00", "10:30"),
            make_block("Meeting", "10:00", "11:00"),
        ])
        result = ScheduleValidator.validate(schedule)
        assert not result.is_valid
        assert any(c.rule == "overlap" for c in result.conflicts)

    def test_adjacent_blocks_no_conflict(self):
        schedule = make_schedule([
            make_block("Study", "09:00", "10:00"),
            make_block("Gym", "10:00", "11:00"),
        ])
        result = ScheduleValidator.validate(schedule)
        assert result.is_valid


class TestSleepBoundary:
    def test_block_before_wake_time(self):
        schedule = make_schedule([
            make_block("Early Task", "05:00", "06:00"),
        ], wake="07:00")
        result = ScheduleValidator.validate(schedule)
        conflicts = [c for c in result.conflicts if c.rule == "sleep_boundary"]
        assert len(conflicts) > 0
        assert conflicts[0].severity == "warning"

    def test_block_after_sleep_time(self):
        schedule = make_schedule([
            make_block("Late Task", "23:30", "23:59"),
        ], wake="07:00", sleep="23:00")
        result = ScheduleValidator.validate(schedule)
        conflicts = [c for c in result.conflicts if c.rule == "sleep_boundary"]
        assert len(conflicts) > 0

    def test_block_within_bounds(self):
        schedule = make_schedule([
            make_block("Normal Task", "10:00", "11:00"),
        ], wake="07:00", sleep="23:00")
        result = ScheduleValidator.validate(schedule)
        assert not any(c.rule == "sleep_boundary" for c in result.conflicts)


class TestDuplicateDetection:
    def test_same_task_id_twice(self):
        task_id = uuid4()
        schedule = make_schedule([
            make_block("Study", "09:00", "10:00", task_id=task_id),
            make_block("Study", "14:00", "15:00", task_id=task_id),
        ])
        result = ScheduleValidator.validate(schedule)
        conflicts = [c for c in result.conflicts if c.rule == "duplicate_task"]
        assert len(conflicts) == 1
        assert conflicts[0].severity == "warning"

    def test_different_task_ids_no_duplicate(self):
        schedule = make_schedule([
            make_block("Study", "09:00", "10:00", task_id=uuid4()),
            make_block("Gym", "14:00", "15:00", task_id=uuid4()),
        ])
        result = ScheduleValidator.validate(schedule)
        assert not any(c.rule == "duplicate_task" for c in result.conflicts)


class TestBufferTime:
    def test_no_buffer_warning(self):
        schedule = make_schedule([
            make_block("Study", "09:00", "10:00"),
            make_block("Gym", "10:03", "11:00"),  # Only 3 min gap
        ])
        result = ScheduleValidator.validate(schedule, buffer_minutes=5)
        assert any(c.rule == "buffer_time" for c in result.conflicts)

    def test_adequate_buffer_no_warning(self):
        schedule = make_schedule([
            make_block("Study", "09:00", "10:00"),
            make_block("Gym", "10:15", "11:00"),  # 15 min gap
        ])
        result = ScheduleValidator.validate(schedule, buffer_minutes=5)
        assert not any(c.rule == "buffer_time" for c in result.conflicts)
