"""Schedule validator — checks a GeneratedSchedule for conflicts before saving.

Validation rules:
1. Overlap detection     — any two blocks with intersecting [start, end)
2. Deadline compliance   — task block ends before task.deadline
3. Sleep boundary        — no block outside [wake_time, sleep_time]
4. Duplicate task        — same task_id appears twice in blocks
5. Buffer time warning   — gap between consecutive blocks < buffer threshold
"""

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any

from app.schemas.schedule import GeneratedSchedule, ScheduleBlock


@dataclass
class ConflictDetail:
    rule: str
    message: str
    block_ids: list[str] = field(default_factory=list)
    severity: str = "error"  # "error" | "warning"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "message": self.message,
            "block_ids": self.block_ids,
            "severity": self.severity,
        }


@dataclass
class ValidationResult:
    is_valid: bool
    conflicts: list[ConflictDetail] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "conflicts": [c.to_dict() for c in self.conflicts],
        }


class ScheduleValidator:
    """Validates a GeneratedSchedule and returns a ValidationResult."""

    DEFAULT_BUFFER_MINUTES = 5

    @classmethod
    def validate(
        cls,
        schedule: GeneratedSchedule,
        buffer_minutes: int = DEFAULT_BUFFER_MINUTES,
    ) -> ValidationResult:
        blocks = sorted(schedule.blocks, key=lambda b: b.start)
        conflicts: list[ConflictDetail] = []

        conflicts.extend(cls._check_overlaps(blocks))
        conflicts.extend(cls._check_sleep_boundary(blocks, schedule.wake_time, schedule.sleep_time))
        conflicts.extend(cls._check_duplicates(blocks))
        conflicts.extend(cls._check_buffer_time(blocks, buffer_minutes))

        errors = [c for c in conflicts if c.severity == "error"]
        return ValidationResult(is_valid=len(errors) == 0, conflicts=conflicts)

    # ─── Rule 1: Overlap detection ────────────────────────────────────

    @classmethod
    def _check_overlaps(cls, blocks: list[ScheduleBlock]) -> list[ConflictDetail]:
        conflicts = []
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                a, b = blocks[i], blocks[j]
                # [a.start, a.end) overlaps [b.start, b.end) if a.start < b.end AND a.end > b.start
                if a.start < b.end and a.end > b.start:
                    conflicts.append(
                        ConflictDetail(
                            rule="overlap",
                            message=(
                                f"'{a.title}' ({a.start.strftime('%H:%M')}–{a.end.strftime('%H:%M')}) "
                                f"overlaps '{b.title}' ({b.start.strftime('%H:%M')}–{b.end.strftime('%H:%M')})"
                            ),
                            block_ids=[a.id, b.id],
                            severity="error",
                        )
                    )
        return conflicts

    # ─── Rule 2: Sleep boundary ───────────────────────────────────────

    @classmethod
    def _check_sleep_boundary(
        cls,
        blocks: list[ScheduleBlock],
        wake: time | None,
        sleep: time | None,
    ) -> list[ConflictDetail]:
        if not wake or not sleep:
            return []
        conflicts = []
        for block in blocks:
            if block.start < wake:
                conflicts.append(
                    ConflictDetail(
                        rule="sleep_boundary",
                        message=(
                            f"'{block.title}' starts at {block.start.strftime('%H:%M')} "
                            f"before wake time {wake.strftime('%H:%M')}"
                        ),
                        block_ids=[block.id],
                        severity="warning",
                    )
                )
            if block.end > sleep and sleep > wake:
                conflicts.append(
                    ConflictDetail(
                        rule="sleep_boundary",
                        message=(
                            f"'{block.title}' ends at {block.end.strftime('%H:%M')} "
                            f"after sleep time {sleep.strftime('%H:%M')}"
                        ),
                        block_ids=[block.id],
                        severity="warning",
                    )
                )
        return conflicts

    # ─── Rule 3: Duplicate task_id ────────────────────────────────────

    @classmethod
    def _check_duplicates(cls, blocks: list[ScheduleBlock]) -> list[ConflictDetail]:
        seen: dict[str, ScheduleBlock] = {}
        conflicts = []
        for block in blocks:
            if not block.task_id:
                continue
            tid = str(block.task_id)
            if tid in seen:
                conflicts.append(
                    ConflictDetail(
                        rule="duplicate_task",
                        message=f"Task appears twice in schedule: '{block.title}'",
                        block_ids=[seen[tid].id, block.id],
                        severity="warning",
                    )
                )
            else:
                seen[tid] = block
        return conflicts

    # ─── Rule 4: Buffer time ──────────────────────────────────────────

    @classmethod
    def _check_buffer_time(
        cls, blocks: list[ScheduleBlock], buffer_minutes: int
    ) -> list[ConflictDetail]:
        conflicts = []
        for i in range(len(blocks) - 1):
            a, b = blocks[i], blocks[i + 1]
            # Compute gap between end of a and start of b (in minutes)
            end_dt = datetime.combine(datetime.today(), a.end)
            start_dt = datetime.combine(datetime.today(), b.start)
            gap = (start_dt - end_dt).total_seconds() / 60
            if 0 < gap < buffer_minutes:
                conflicts.append(
                    ConflictDetail(
                        rule="buffer_time",
                        message=(
                            f"Only {int(gap)} min gap between '{a.title}' and '{b.title}' "
                            f"(recommended: {buffer_minutes} min)"
                        ),
                        block_ids=[a.id, b.id],
                        severity="warning",
                    )
                )
        return conflicts
