"""AI API endpoints — routine parsing, analysis, chat assistant, suggestions."""

from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.api.deps import CurrentUser, DbSession
from app.core.rate_limit import limiter
from app.schemas.schedule import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    ChatRequest,
    ChatResponse,
    ParsedRoutine,
    ParseRoutineRequest,
)
from app.schemas.base import ApiResponse
from app.services.ai.analyze_service import AIAnalyzeService
from app.services.ai.routine_parser import AIRoutineParserService
from app.services.ai.scheduler_agent import AISchedulerAgent

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post(
    "/parse-routine",
    response_model=ApiResponse[ParsedRoutine],
    summary="Parse a routine description",
)
@limiter.limit("10/minute")
async def parse_routine(
    request: Request,
    data: ParseRoutineRequest,
    current_user: CurrentUser,
):
    """Parse a natural language routine description into structured events and flexible tasks.

    Falls back to rule-based parsing if the AI is unavailable or returns invalid JSON.
    """
    service = AIRoutineParserService()
    result = await service.parse_routine(data)
    return ApiResponse(data=result)


@router.post(
    "/analyze",
    response_model=ApiResponse[AIAnalyzeResponse],
    summary="Analyse a routine and extract tasks",
)
@limiter.limit("5/minute")
async def analyze(
    request: Request,
    data: AIAnalyzeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Analyse a routine description and extract structured tasks.

    Set `auto_persist=true` to automatically save extracted tasks to the database.
    """
    service = AIAnalyzeService(db)
    result = await service.analyze(current_user.id, data)
    return ApiResponse(data=result)


@router.post(
    "/chat",
    response_model=ApiResponse[ChatResponse],
    summary="Chat with the AI assistant",
)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    data: ChatRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """Send a message to the AI scheduling assistant.

    The assistant can:
    - Create, update, and delete tasks
    - Reschedule tasks to new time slots
    - Regenerate today's schedule
    - Find free time slots
    - Search tasks by keyword
    - Move tasks to different dates

    Optionally pass `conversation_id` to continue a specific conversation.
    """
    agent = AISchedulerAgent(db)
    result = await agent.chat(current_user, data.conversation_id, data)
    return ApiResponse(data=result)


@router.get(
    "/chat/conversations",
    summary="List AI conversations",
)
async def list_conversations(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(20, ge=1, le=100),
):
    """Return a list of the user's AI conversations, newest first."""
    agent = AISchedulerAgent(db)
    conversations = await agent.list_conversations(current_user.id, limit)
    return ApiResponse(data={"conversations": conversations})


@router.post(
    "/chat/new",
    summary="Start a new conversation",
)
async def new_conversation(
    current_user: CurrentUser,
    db: DbSession,
    title: str | None = Query(None, max_length=255),
):
    """Explicitly start a new AI conversation. Returns the conversation ID."""
    agent = AISchedulerAgent(db)
    result = await agent.create_new_conversation(current_user.id, title)
    return ApiResponse(data=result)


@router.get(
    "/suggestions",
    summary="Get AI scheduling suggestions",
)
async def get_suggestions(current_user: CurrentUser, db: DbSession):
    """Return proactive scheduling suggestions based on the user's habit profile.

    Suggestions include preferred task times, buffer recommendations,
    and consistency feedback based on completion history.
    """
    from app.services.habits.habit_service import HabitService

    habit_service = HabitService(db)
    suggestions = await habit_service.get_suggestions(current_user.id)
    return ApiResponse(data={"suggestions": suggestions})
