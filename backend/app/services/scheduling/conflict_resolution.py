from datetime import datetime, timedelta

from app.schemas.schedule import GeneratedSchedule


class ConflictResolutionService:
    """
    Analyzes a GeneratedSchedule and provides suggestions or warnings
    if there are unscheduled tasks or overlaps.
    """

    @staticmethod
    def analyze_schedule(schedule: GeneratedSchedule) -> list[str]:
        suggestions = []

        # Check if there are any unscheduled tasks
        if schedule.unscheduled_tasks:
            count = len(schedule.unscheduled_tasks)
            task_list = ", ".join(schedule.unscheduled_tasks[:3])
            if count > 3:
                task_list += f" and {count - 3} more"

            suggestions.append(
                f"You have {count} unscheduled tasks (e.g., {task_list}). "
                "Consider moving them to another day, breaking them into smaller chunks, or reducing your planned durations."
            )

        # Check for gaps and overlaps (even though the pipeline shouldn't produce overlaps, it's good to verify)
        blocks = sorted(schedule.blocks, key=lambda b: b.start)
        total_scheduled_minutes = 0

        for i in range(len(blocks) - 1):
            current = blocks[i]
            nxt = blocks[i + 1]

            # Simple duration calculation (assuming no cross-day blocks for simplicity)
            current_duration = (
                datetime.combine(schedule.date, current.end)
                - datetime.combine(schedule.date, current.start)
            ).total_seconds() / 60
            total_scheduled_minutes += current_duration

            if current.end > nxt.start:
                suggestions.append(
                    f"Conflict detected between '{current.title}' (ends at {current.end.strftime('%H:%M')}) "
                    f"and '{nxt.title}' (starts at {nxt.start.strftime('%H:%M')})."
                )

        # Add duration of the last block
        if blocks:
            last = blocks[-1]
            last_duration = (
                datetime.combine(schedule.date, last.end)
                - datetime.combine(schedule.date, last.start)
            ).total_seconds() / 60
            total_scheduled_minutes += last_duration

        # Check total scheduled time against wake window
        if schedule.wake_time and schedule.sleep_time:
            wake_dt = datetime.combine(schedule.date, schedule.wake_time)
            sleep_dt = datetime.combine(schedule.date, schedule.sleep_time)
            if sleep_dt <= wake_dt:
                sleep_dt += timedelta(days=1)

            total_available_minutes = (sleep_dt - wake_dt).total_seconds() / 60

            if total_scheduled_minutes > total_available_minutes * 0.9:
                suggestions.append(
                    "Your schedule is extremely packed! You have scheduled over 90% of your waking hours. "
                    "Consider adding more breaks or moving non-urgent tasks to another day to avoid burnout."
                )

        return suggestions
