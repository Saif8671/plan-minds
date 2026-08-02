from app.models import RecurrenceType, Task, TaskStatus


class AISuggestionService:
    def generate_suggestions(self, tasks: list[Task]) -> list[str]:
        suggestions: list[str] = []

        skipped = [task for task in tasks if task.status == TaskStatus.SKIPPED]
        completed = [task for task in tasks if task.status == TaskStatus.COMPLETED]
        pending = [
            task
            for task in tasks
            if task.status in {TaskStatus.PENDING, TaskStatus.IN_PROGRESS}
        ]

        if skipped:
            skipped_titles = ", ".join(task.title for task in skipped[:3])
            suggestions.append(
                f"You skipped {skipped_titles}. Try batching those into a lighter morning block to keep momentum."
            )

        if not completed:
            suggestions.append(
                "Start with one high-priority task today to build consistency before adding more."
            )

        if len(pending) >= 4:
            suggestions.append(
                "You have several open tasks. Focus on the top 2 priorities and leave the rest for later."
            )

        if any(task.category.value == "study" for task in completed):
            suggestions.append(
                "Your study sessions are working well. Keep the next block protected from distractions."
            )

        if any(task.recurrence == RecurrenceType.DAILY for task in tasks):
            suggestions.append(
                "Recurring habits are strong anchors; keep your daily routine visible at the same time each day."
            )

        return suggestions
