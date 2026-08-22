from app.schemas.schedule import AIAnalyzeTask


class MissingFieldDetector:
    @staticmethod
    def detect_missing_fields(task: AIAnalyzeTask) -> list[str]:
        missing = []

        # If it has a start time, it needs an end time or duration
        if task.start and not task.end and not task.duration:
            missing.append("duration")

        # If it doesn't have a start time, it MUST have a duration
        if not task.start and not task.duration:
            missing.append("duration")

        # If it's recurring, it might need a rule, but we don't strictly enforce it here unless we have a partial rule

        return missing


class QuestionGenerator:
    @staticmethod
    def generate_question(task_title: str, missing_fields: list[str]) -> str:
        if not missing_fields:
            return ""

        questions = []
        for field in missing_fields:
            if field == "duration":
                questions.append(f"How long will '{task_title}' take?")
            elif field == "start":
                questions.append(f"What time does '{task_title}' start?")

        if len(questions) == 1:
            return questions[0]

        return " ".join(questions)


class ClarificationService:
    def __init__(self):
        self.detector = MissingFieldDetector()
        self.generator = QuestionGenerator()

    def clarify_task(self, task: AIAnalyzeTask) -> str | None:
        missing = self.detector.detect_missing_fields(task)
        if not missing:
            return None
        return self.generator.generate_question(task.title, missing)
