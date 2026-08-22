"""AI Scheduler Agent — conversational interface to the task/schedule system.

Tools available to the AI:
  - get_tasks           — list user's pending tasks
  - create_task         — create a new task
  - update_task         — update task fields
  - delete_task         — delete a task
  - reschedule_task     — move a task's time slot
  - reschedule_day      — regenerate today's schedule
  - find_free_slot      — find next free N-minute window
  - search_tasks        — search tasks by keyword
  - move_task_to_date   — update task deadline/fixed time to another day
"""

import json
from datetime import UTC, datetime
from uuid import UUID

from groq import AsyncGroq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logger import get_logger
from app.models import (
    Conversation,
    ConversationMessage,
    ConversationStatus,
    Task,
    TaskStatus,
)
from app.repositories.task_repository import TaskRepository
from app.schemas.schedule import ChatRequest, ChatResponse

logger = get_logger(__name__)
settings = get_settings()

# ─── Tool definitions ──────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Get the user's current pending tasks",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "duration": {
                        "type": "integer",
                        "description": "Duration in minutes",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "work",
                            "study",
                            "health",
                            "personal",
                            "meal",
                            "sleep",
                            "other",
                        ],
                    },
                    "deadline": {
                        "type": "string",
                        "description": "ISO datetime deadline, e.g. 2026-08-10T17:00:00",
                    },
                    "is_fixed": {
                        "type": "boolean",
                        "description": "Whether the task has a fixed time",
                    },
                    "fixed_start": {
                        "type": "string",
                        "description": "HH:MM format start time",
                    },
                    "fixed_end": {
                        "type": "string",
                        "description": "HH:MM format end time",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's fields",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task UUID"},
                    "title": {"type": "string"},
                    "duration": {"type": "integer"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                    },
                    "deadline": {"type": "string", "description": "ISO datetime"},
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task UUID to delete"}
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_task",
            "description": "Move a task to a new fixed start/end time",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "new_start": {"type": "string", "description": "HH:MM"},
                    "new_end": {"type": "string", "description": "HH:MM"},
                },
                "required": ["task_id", "new_start", "new_end"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_day",
            "description": "Regenerate today's entire schedule",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_free_slot",
            "description": "Find the next available free time slot of a given duration",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Required free time in minutes",
                    }
                },
                "required": ["duration_minutes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search tasks by keyword in title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "move_task_to_date",
            "description": "Move a task's deadline/fixed time to a different date",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "target_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
                "required": ["task_id", "target_date"],
            },
        },
    },
]

# ─── Conversation history cap ──────────────────────────────────────────
_MAX_HISTORY = 20


class AISchedulerAgent:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.client = (
            AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None
        )

    def _build_system_prompt(self, user, tasks: list[Task]) -> str:
        now = datetime.now(UTC)
        tz = getattr(user, "timezone", "UTC")
        pending_count = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        task_summary = ", ".join(f"'{t.title}'" for t in tasks[:5])
        if len(tasks) > 5:
            task_summary += f" and {len(tasks) - 5} more"

        return f"""You are PlanMinds, a smart productivity assistant. Help the user manage their tasks and schedule.

Today: {now.strftime("%A, %Y-%m-%d")}
Current time: {now.strftime("%H:%M")} UTC
User timezone: {tz}
Pending tasks ({pending_count}): {task_summary or "none"}

Guidelines:
- Be concise and action-oriented
- Call a tool BEFORE explaining what you did
- When the user asks to reschedule, move, or update a task — do it, then confirm
- If the user provides a list of tasks or a schedule, parse it and use the 'create_task' tool multiple times to add each of them. Use 'is_fixed', 'fixed_start', and 'fixed_end' for tasks with specific times.
- If you need a task ID and it's ambiguous, ask the user to clarify which task
- Always speak in first person: "I've moved your gym session..."
"""

    async def chat(
        self, user, conversation_id: UUID | None, data: ChatRequest
    ) -> ChatResponse:
        """Process a chat message, execute tool calls, and return the assistant reply."""
        if not self.client:
            return ChatResponse(
                reply="AI assistant is not configured. Please set GROQ_API_KEY."
            )

        # Load or create conversation
        conversation = await self._get_or_create_conversation(user.id, conversation_id)

        # Build message history (capped at _MAX_HISTORY)
        messages = await self._build_message_history(conversation, user)

        # Append user message
        messages.append({"role": "user", "content": data.message})
        user_msg = ConversationMessage(
            conversation_id=conversation.id,
            role="user",
            content=data.message,
        )
        self.db.add(user_msg)

        tasks = await self.task_repo.get_by_user(user.id, limit=200)

        # Inject rich system prompt
        messages[0] = {
            "role": "system",
            "content": self._build_system_prompt(user, tasks),
        }

        # Tool execution loop
        actions_taken: list[str] = []
        for _ in range(5):  # Max 5 tool calls per turn
            try:
                response = await self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0.3,
                    max_tokens=1024,
                )
            except Exception as exc:
                logger.error("Groq API error: %s", exc)
                reply = "I'm sorry, I encountered an error while processing your request. Please try again."
                assistant_msg = ConversationMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=reply,
                )
                self.db.add(assistant_msg)
                conversation.updated_at = datetime.now(UTC)
                await self.db.flush()
                return ChatResponse(
                    reply=reply, actions_taken=actions_taken if actions_taken else None
                )

            msg = response.choices[0].message

            if not msg.tool_calls:
                # Final text response
                reply = msg.content or "Done!"
                assistant_msg = ConversationMessage(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=reply,
                )
                self.db.add(assistant_msg)
                conversation.updated_at = datetime.now(UTC)
                await self.db.flush()
                return ChatResponse(
                    reply=reply, actions_taken=actions_taken if actions_taken else None
                )

            # Process tool calls
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
                }
            )
            for tool_call in msg.tool_calls:
                result = await self._execute_tool(
                    tool_call.function.name,
                    tool_call.function.arguments,
                    user,
                    tasks,
                    actions_taken,
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result),
                    }
                )

        return ChatResponse(
            reply="I've processed your request.", actions_taken=actions_taken
        )

    async def _execute_tool(
        self,
        name: str,
        args_str: str,
        user,
        tasks: list[Task],
        actions_taken: list[str],
    ) -> dict:
        """Dispatch a single tool call and return the result dict."""
        try:
            args = json.loads(args_str) if args_str else {}
        except json.JSONDecodeError:
            return {"error": "Invalid tool arguments"}

        try:
            if name == "get_tasks":
                return await self._exec_get_tasks(user.id)
            elif name == "create_task":
                return await self._exec_create_task(user.id, args, actions_taken)
            elif name == "update_task":
                return await self._exec_update_task(user.id, args, actions_taken)
            elif name == "delete_task":
                return await self._exec_delete_task(user.id, args, actions_taken)
            elif name == "reschedule_task":
                return await self._exec_reschedule_task(user.id, args, actions_taken)
            elif name == "reschedule_day":
                return await self._exec_reschedule_day(user, actions_taken)
            elif name == "find_free_slot":
                return await self._exec_find_free_slot(user.id, args)
            elif name == "search_tasks":
                return await self._exec_search_tasks(user.id, args)
            elif name == "move_task_to_date":
                return await self._exec_move_task_to_date(user.id, args, actions_taken)
            else:
                return {"error": f"Unknown tool: {name}"}
        except Exception as exc:
            logger.warning("Tool %s failed: %s", name, exc)
            return {"error": str(exc)}

    # ─── Tool implementations ─────────────────────────────────────────

    async def _exec_get_tasks(self, user_id: UUID) -> dict:
        tasks = await self.task_repo.get_by_user(
            user_id, limit=50, status=TaskStatus.PENDING
        )
        return {
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "priority": t.priority.value if t.priority else None,
                    "duration": t.duration,
                    "deadline": t.deadline.isoformat() if t.deadline else None,
                }
                for t in tasks
            ]
        }

    async def _exec_create_task(
        self, user_id: UUID, args: dict, actions_taken: list[str]
    ) -> dict:
        from datetime import time

        from app.models import Task, TaskCategory, TaskPriority

        task = Task(
            user_id=user_id,
            title=args.get("title", "Untitled"),
            duration=args.get("duration", 60),
            priority=TaskPriority(args.get("priority", "medium")),
            category=TaskCategory(args.get("category", "other")),
            is_fixed=args.get("is_fixed", False),
        )
        if args.get("deadline"):
            try:
                task.deadline = datetime.fromisoformat(args["deadline"])
            except ValueError:
                pass

        if args.get("is_fixed") and args.get("fixed_start") and args.get("fixed_end"):
            for time_str in (args.get("fixed_start"), args.get("fixed_end")):
                pass  # just a placeholder for loop syntax

            def parse_time(ts: str):
                ts = ts.strip().upper()
                try:
                    return time.fromisoformat(ts)
                except ValueError:
                    try:
                        from datetime import datetime

                        return datetime.strptime(ts, "%I:%M %p").time()
                    except ValueError:
                        return None

            fs = parse_time(args.get("fixed_start"))
            fe = parse_time(args.get("fixed_end"))
            if fs and fe:
                task.fixed_start = fs
                task.fixed_end = fe

        task = await self.task_repo.create(task)
        actions_taken.append(f"Created task: '{task.title}'")
        await self.db.flush()
        return {"task_id": str(task.id), "title": task.title, "status": "created"}

    async def _exec_update_task(
        self, user_id: UUID, args: dict, actions_taken: list[str]
    ) -> dict:
        from app.models import TaskPriority

        task_id_str = args.get("task_id", "")
        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id"}

        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return {"error": "Task not found"}

        if "title" in args:
            task.title = args["title"]
        if "duration" in args:
            task.duration = int(args["duration"])
        if "priority" in args:
            try:
                task.priority = TaskPriority(args["priority"])
            except ValueError:
                pass
        if "deadline" in args and args["deadline"]:
            try:
                task.deadline = datetime.fromisoformat(args["deadline"])
            except ValueError:
                pass

        await self.task_repo.update(task)
        actions_taken.append(f"Updated task: '{task.title}'")
        return {"task_id": str(task.id), "status": "updated"}

    async def _exec_delete_task(
        self, user_id: UUID, args: dict, actions_taken: list[str]
    ) -> dict:
        task_id_str = args.get("task_id", "")
        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id"}

        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return {"error": "Task not found"}

        title = task.title
        await self.task_repo.delete(task)
        actions_taken.append(f"Deleted task: '{title}'")
        return {"status": "deleted", "title": title}

    async def _exec_reschedule_task(
        self, user_id: UUID, args: dict, actions_taken: list[str]
    ) -> dict:
        from datetime import time

        task_id_str = args.get("task_id", "")
        try:
            task_id = UUID(task_id_str)
        except ValueError:
            return {"error": "Invalid task_id"}

        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return {"error": "Task not found"}

        try:
            new_start = time.fromisoformat(args.get("new_start", ""))
            new_end = time.fromisoformat(args.get("new_end", ""))
        except ValueError:
            return {"error": "Invalid time format. Use HH:MM"}

        task.is_fixed = True
        task.fixed_start = new_start
        task.fixed_end = new_end
        await self.task_repo.update(task)
        actions_taken.append(
            f"Rescheduled '{task.title}' to {args['new_start']}–{args['new_end']}"
        )
        return {
            "status": "rescheduled",
            "new_start": str(new_start),
            "new_end": str(new_end),
        }

    async def _exec_reschedule_day(self, user, actions_taken: list[str]) -> dict:
        try:
            from app.schemas.schedule import ScheduleRegenerateRequest
            from app.services.scheduling.engine import SchedulingEngine

            engine = SchedulingEngine(self.db)
            await engine.regenerate(user, ScheduleRegenerateRequest())
            actions_taken.append("Regenerated today's schedule")
            return {"status": "regenerated"}
        except Exception as exc:
            return {"error": str(exc)}

    async def _exec_find_free_slot(self, user_id: UUID, args: dict) -> dict:
        from datetime import date, time

        duration = args.get("duration_minutes", 30)

        # Get today's schedule
        result = await self.db.execute(
            select(__import__("app.models", fromlist=["Schedule"]).Schedule)
            .where(
                __import__("app.models", fromlist=["Schedule"]).Schedule.user_id
                == user_id,
                __import__("app.models", fromlist=["Schedule"]).Schedule.date
                == date.today(),
            )
            .order_by(
                __import__(
                    "app.models", fromlist=["Schedule"]
                ).Schedule.created_at.desc()
            )
            .limit(1)
        )
        schedule = result.scalar_one_or_none()
        if not schedule or not schedule.generated_schedule:
            return {"message": "No schedule for today. You're free all day!"}

        blocks = sorted(
            schedule.generated_schedule.get("blocks", []),
            key=lambda b: b.get("start", "00:00"),
        )

        cursor = time(8, 0)  # Start searching from 8am
        for block in blocks:
            try:
                block_start = time.fromisoformat(block["start"])
                block_end = time.fromisoformat(block["end"])
            except (ValueError, KeyError):
                continue

            gap_minutes = (
                datetime.combine(date.today(), block_start)
                - datetime.combine(date.today(), cursor)
            ).total_seconds() / 60

            if gap_minutes >= duration:
                return {
                    "free_slot": {
                        "start": cursor.strftime("%H:%M"),
                        "end": (
                            datetime.combine(date.today(), cursor)
                            + __import__("datetime").timedelta(minutes=duration)
                        )
                        .time()
                        .strftime("%H:%M"),
                        "duration_minutes": duration,
                    }
                }
            cursor = block_end

        # Check after last block
        end_of_day = time(22, 0)
        remaining = (
            datetime.combine(date.today(), end_of_day)
            - datetime.combine(date.today(), cursor)
        ).total_seconds() / 60
        if remaining >= duration:
            return {
                "free_slot": {
                    "start": cursor.strftime("%H:%M"),
                    "end": (
                        datetime.combine(date.today(), cursor)
                        + __import__("datetime").timedelta(minutes=duration)
                    )
                    .time()
                    .strftime("%H:%M"),
                    "duration_minutes": duration,
                }
            }

        return {"message": f"No free {duration}-minute slot found in today's schedule"}

    async def _exec_search_tasks(self, user_id: UUID, args: dict) -> dict:
        query = args.get("query", "").lower().strip()
        if not query:
            return {"error": "Search query is required"}

        tasks = await self.task_repo.get_by_user(user_id, limit=500)
        matched = [
            t
            for t in tasks
            if query in t.title.lower()
            or (t.description and query in t.description.lower())
        ]
        return {
            "tasks": [
                {
                    "id": str(t.id),
                    "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority.value,
                }
                for t in matched[:10]
            ],
            "total_found": len(matched),
        }

    async def _exec_move_task_to_date(
        self, user_id: UUID, args: dict, actions_taken: list[str]
    ) -> dict:
        from datetime import date

        task_id_str = args.get("task_id", "")
        target_date_str = args.get("target_date", "")

        try:
            task_id = UUID(task_id_str)
            target_date = date.fromisoformat(target_date_str)
        except (ValueError, TypeError):
            return {"error": "Invalid task_id or target_date. Use YYYY-MM-DD format."}

        task = await self.task_repo.get_by_id_and_user(task_id, user_id)
        if not task:
            return {"error": "Task not found"}

        if task.deadline:
            task.deadline = datetime.combine(target_date, task.deadline.timetz())
        elif task.fixed_start:
            task.fixed_start = (
                task.fixed_start
            )  # Keep the time, date changes via deadline
            # For fixed tasks, set a new deadline
            task.deadline = datetime.combine(target_date, task.fixed_start)

        await self.task_repo.update(task)
        actions_taken.append(f"Moved '{task.title}' to {target_date_str}")
        return {
            "status": "moved",
            "task_id": str(task.id),
            "target_date": target_date_str,
        }

    # ─── Conversation management ──────────────────────────────────────

    async def _get_or_create_conversation(
        self, user_id: UUID, conversation_id: UUID | None
    ) -> Conversation:
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id,
                    Conversation.status == ConversationStatus.ACTIVE,
                )
            )
            conv = result.scalar_one_or_none()
            if conv:
                return conv

        # Try to find the most recent active conversation
        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.status == ConversationStatus.ACTIVE,
            )
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

        # Create a new conversation
        new_conv = Conversation(
            user_id=user_id,
            title=f"Conversation {datetime.now(UTC).strftime('%b %d')}",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(new_conv)
        await self.db.flush()
        await self.db.refresh(new_conv)
        return new_conv

    async def _build_message_history(
        self, conversation: Conversation, user
    ) -> list[dict]:
        """Build the messages array for the Groq API call."""
        result = await self.db.execute(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation.id)
            .order_by(ConversationMessage.created_at.asc())
        )
        db_messages = result.scalars().all()

        # Cap history
        if len(db_messages) > _MAX_HISTORY:
            db_messages = db_messages[-_MAX_HISTORY:]

        messages = [
            {"role": "system", "content": ""}
        ]  # Placeholder — replaced before API call
        for msg in db_messages:
            messages.append({"role": msg.role, "content": msg.content})

        return messages

    async def list_conversations(self, user_id: UUID, limit: int = 20) -> list[dict]:
        """Return a list of the user's conversations."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        convs = result.scalars().all()
        return [
            {
                "id": str(c.id),
                "title": c.title,
                "status": c.status.value,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat(),
            }
            for c in convs
        ]

    async def create_new_conversation(
        self, user_id: UUID, title: str | None = None
    ) -> dict:
        """Explicitly start a new conversation."""
        conv = Conversation(
            user_id=user_id,
            title=title
            or f"New conversation {datetime.now(UTC).strftime('%b %d %H:%M')}",
            status=ConversationStatus.ACTIVE,
        )
        self.db.add(conv)
        await self.db.flush()
        await self.db.refresh(conv)
        return {
            "id": str(conv.id),
            "title": conv.title,
            "status": conv.status.value,
            "created_at": conv.created_at.isoformat(),
        }
