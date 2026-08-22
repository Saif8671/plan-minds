import datetime as dt
from datetime import datetime, time

from dateutil.rrule import rrulestr

from app.models import Task


class RecurrenceExpander:
    """
    Expands a recurring Task into specific occurrences based on an RRULE string.
    """

    @staticmethod
    def expand_task_for_date(task: Task, target_date: dt.date) -> list[datetime]:
        """
        Returns a list of datetime occurrences for the given task on the target_date.
        If the task does not occur on the target_date, returns an empty list.
        """
        if not task.is_recurring or not task.recurrence_rule:
            return []

        rule_str = task.recurrence_rule.get("rrule")
        if not rule_str:
            return []

        try:
            # We need a start date to evaluate the rrule
            # If the task has a deadline or was created on a specific date, we use that.
            # Otherwise we use the task's created_at date.
            dtstart = task.created_at or datetime.utcnow()

            # rrulestr requires dtstart, we pass it via kwargs or it uses now
            # To be safe and evaluate across timezones properly, we map everything to midnight
            # of the target_date for checking bounds.
            start_of_day = datetime.combine(target_date, time.min)
            end_of_day = datetime.combine(target_date, time.max)

            # Combine the rule string with DTSTART if it doesn't have it
            if "DTSTART" not in rule_str.upper():
                dtstart_str = dtstart.strftime("%Y%m%dT%H%M%S")
                rule_str = f"DTSTART:{dtstart_str}\n{rule_str}"

            rule = rrulestr(rule_str)

            # Get all occurrences between start_of_day and end_of_day
            occurrences = rule.between(start_of_day, end_of_day, inc=True)
            return occurrences
        except Exception as e:
            # If parsing fails, just return empty to avoid crashing the scheduler
            import logging

            logging.error(f"Failed to expand recurrence rule: {e}")
            return []
