import json
from datetime import time
from uuid import UUID

from groq import AsyncGroq
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ExternalServiceError
from app.core.logger import get_logger
from app.models import Task
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.schedule import (
    ChatRequest,
    ChatResponse,
    ParseRoutineRequest,
    ScheduleGenerateRequest,
)
from app.services.ai.routine_parser import AIRoutineParserService
from app.services.scheduling.engine import SchedulingEngine

logger = get_logger(__name__)
settings = get_settings()


class AIChatService:
    def __init__(self, db: AsyncSession, user_id: UUID):
        self.db = db
        self.user_id = user_id
        self.client = (
            AsyncGroq(
                api_key=settings.groq_api_key,
            )
            if settings.groq_api_key
            else None
        )

    async def chat(self, data: ChatRequest) -> ChatResponse:
        if not self.client:
            return ChatResponse(
                reply="AI chat requires an API key. Configure GROQ_API_KEY in your environment.",
                suggested_actions=["Configure API key", "Use parse-routine endpoint"],
            )

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "reschedule_task",
                    "description": "Reschedule an existing task to a new time",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to reschedule (from context)",
                            },
                            "new_time": {
                                "type": "string",
                                "description": "The new start time in HH:MM format",
                            },
                        },
                        "required": ["task_id", "new_time"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the task",
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Duration in minutes",
                            },
                            "fixed_start": {
                                "type": "string",
                                "description": "Start time in HH:MM format if fixed, otherwise omit",
                            },
                        },
                        "required": ["title", "duration"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "The ID of the task to delete (from context)",
                            },
                        },
                        "required": ["task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_daily_schedule",
                    "description": "Generate a full daily schedule from a single prompt or routine description. Ask for clarification if needed.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "routine_description": {
                                "type": "string",
                                "description": "The routine description provided by the user.",
                            }
                        },
                        "required": ["routine_description"],
                    },
                },
            },
        ]

        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful schedule and productivity assistant. Use the provided tools to create, reschedule, or delete tasks if the user asks. If you modify a task, tell the user.",
                },
                {"role": "user", "content": data.message},
            ]
            if data.context:
                messages.insert(
                    1,
                    {
                        "role": "system",
                        "content": f"Context (Today's Tasks): {json.dumps(data.context)}",
                    },
                )

            response = await self.client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=500,
            )

            response_message = response.choices[0].message

            if response_message.tool_calls:
                task_repo = TaskRepository(self.db)
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "reschedule_task":
                        args = json.loads(tool_call.function.arguments)
                        t_id = args.get("task_id")
                        new_time = args.get("new_time")
                        if t_id and new_time:
                            hour, minute = map(int, new_time.split(":"))
                            task = await task_repo.get_by_id_and_user(
                                UUID(t_id), self.user_id
                            )
                            if task:
                                await task_repo.update(
                                    task,
                                    obj_in={
                                        "is_fixed": True,
                                        "fixed_start": time(hour, minute),
                                    },
                                )
                    elif tool_call.function.name == "create_task":
                        args = json.loads(tool_call.function.arguments)
                        
                        task_obj = Task(
                            user_id=self.user_id,
                            title=args.get("title"),
                            duration=args.get("duration"),
                        )
                        if args.get("fixed_start"):
                            hour, minute = map(int, args.get("fixed_start").split(":"))
                            task_obj.is_fixed = True
                            task_obj.fixed_start = time(hour, minute)

                        await task_repo.create(task_obj)
                    elif tool_call.function.name == "delete_task":
                        args = json.loads(tool_call.function.arguments)
                        t_id = args.get("task_id")
                        if t_id:
                            task = await task_repo.get_by_id_and_user(
                                UUID(t_id), self.user_id
                            )
                            if task:
                                await task_repo.delete(task)
                    elif tool_call.function.name == "generate_daily_schedule":
                        args = json.loads(tool_call.function.arguments)
                        routine_desc = args.get("routine_description")
                        if routine_desc:
                            user_repo = UserRepository(self.db)
                            user = await user_repo.get_by_id(self.user_id)
                            if user:
                                parser_service = AIRoutineParserService()
                                parsed = await parser_service.parse_routine(
                                    ParseRoutineRequest(routine_text=routine_desc)
                                )
                                engine = SchedulingEngine(self.db)
                                await engine.generate(
                                    user,
                                    ScheduleGenerateRequest(include_parsed_routine=parsed),
                                )

                return ChatResponse(reply="I've updated your schedule as requested!")

            reply = response_message.content or "I couldn't generate a response."
            return ChatResponse(reply=reply)
        except Exception as exc:
            logger.error(f"AI chat error: {exc}")
            raise ExternalServiceError("AI", str(exc)) from exc
