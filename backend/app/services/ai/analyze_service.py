import json
from datetime import datetime
from uuid import UUID

from groq import AsyncGroq
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.core.logger import get_logger
from app.models import AIAnalysis, Task, TaskCategory, TaskPriority
from app.repositories.task_repository import TaskRepository
from app.schemas.schedule import AIAnalyzeRequest, AIAnalyzeResponse, AIAnalyzeTask
from app.services.ai.routine_parser import AIRoutineParserService

logger = get_logger(__name__)
settings = get_settings()

ANALYZE_PROMPT = """You are a schedule analysis assistant. Parse the user's daily routine description and extract structured tasks.

Return ONLY valid JSON with this exact schema:
{
  "tasks": [
    {
      "title": "Task name",
      "start": "HH:MM" or null,
      "end": "HH:MM" or null,
      "duration": minutes_int or null,
      "category": "work|study|health|personal|meal|sleep|other" or null,
      "priority": "low|medium|high|urgent" or null,
      "deadline": "YYYY-MM-DDTHH:MM:SS" or null,
      "is_recurring": true or false,
      "recurrence_rule": "RFC5545 RRULE string" or null
    }
  ],
  "wake_time": "HH:MM" or null,
  "sleep_time": "HH:MM" or null,
  "notes": "string or null"
}

Rules:
- Convert all times to 24-hour HH:MM format
- Duration is in minutes
- For events with time ranges (e.g., "Gym from 8 to 9"), set start and end
- For flexible tasks (e.g., "Study 2 hours"), set duration only
- Infer categories from context
- If user mentions deadlines (e.g. "by friday"), convert to a reasonable ISO timestamp (assumed next occurrence)
- If task repeats (e.g. "every day"), set is_recurring=true and provide an RFC5545 RRULE (e.g., FREQ=DAILY)
"""


class AIAnalyzeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = (
            AsyncGroq(
                api_key=settings.groq_api_key,
            )
            if settings.groq_api_key
            else None
        )

    async def analyze(self, user_id: UUID, data: AIAnalyzeRequest) -> AIAnalyzeResponse:
        if self.client:
            result = await self._analyze_with_ai(data)
        else:
            result = self._analyze_with_rules(data)

        # Persist the analysis
        analysis = AIAnalysis(
            user_id=user_id,
            input_text=data.text,
            analysis_result=result.model_dump(mode="json"),
            model_used=settings.groq_model if self.client else "rule-based",
        )
        self.db.add(analysis)
        
        if data.auto_persist:
            await self._persist_tasks(user_id, result.tasks)
            
        await self.db.commit()

        return result

    def _validate_task(self, task: AIAnalyzeTask) -> None:
        if not task.title:
            raise ValidationError("Task title is required")
        if task.duration is not None and task.duration <= 0:
            raise ValidationError("Task duration must be strictly positive")

    async def _persist_tasks(self, user_id: UUID, tasks: list[AIAnalyzeTask]) -> None:
        task_repo = TaskRepository(self.db)
        for t in tasks:
            self._validate_task(t)
            
            # Convert string priority to enum
            priority_val = TaskPriority.MEDIUM
            if t.priority:
                try:
                    priority_val = TaskPriority(t.priority.lower())
                except ValueError:
                    pass
            
            # Convert string category to enum
            category_val = TaskCategory.OTHER
            if t.category:
                try:
                    category_val = TaskCategory(t.category.lower())
                except ValueError:
                    pass

            db_task = Task(
                user_id=user_id,
                title=t.title,
                duration=t.duration,
                category=category_val,
                priority=priority_val,
                is_recurring=t.is_recurring,
                recurrence_rule={"rrule": t.recurrence_rule} if t.recurrence_rule else None,
                deadline=t.deadline,
            )
            
            if t.start and t.end:
                try:
                    start_time = datetime.strptime(t.start, "%H:%M").time()
                    end_time = datetime.strptime(t.end, "%H:%M").time()
                    db_task.is_fixed = True
                    db_task.fixed_start = start_time
                    db_task.fixed_end = end_time
                except ValueError:
                    pass
                    
            self.db.add(db_task)

    async def _analyze_with_ai(self, data: AIAnalyzeRequest) -> AIAnalyzeResponse:
        try:
            response = await self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": ANALYZE_PROMPT},
                    {
                        "role": "user",
                        "content": f"Timezone: {data.timezone}\n\nRoutine:\n{data.text}",
                    },
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return AIAnalyzeResponse.model_validate(parsed)
        except Exception as exc:
            logger.warning("AI analysis failed, falling back to rules: %s", exc)
            return self._analyze_with_rules(data)

    def _analyze_with_rules(self, data: AIAnalyzeRequest) -> AIAnalyzeResponse:
        # Use the existing rule-based parser
        parser = AIRoutineParserService()

        parsed = parser._parse_with_rules(data.text)

        tasks = []
        for event in parsed.fixed_events:
            tasks.append(
                AIAnalyzeTask(
                    title=event.title,
                    start=event.start.strftime("%H:%M") if event.start else None,
                    end=event.end.strftime("%H:%M") if event.end else None,
                    category=event.category,
                )
            )

        for flex in parsed.flexible_tasks:
            tasks.append(
                AIAnalyzeTask(
                    title=flex.title,
                    duration=flex.duration,
                    category=flex.category,
                    priority=flex.priority,
                )
            )

        return AIAnalyzeResponse(
            tasks=tasks,
            wake_time=parsed.wake_time.strftime("%H:%M") if parsed.wake_time else None,
            sleep_time=(
                parsed.sleep_time.strftime("%H:%M") if parsed.sleep_time else None
            ),
        )
