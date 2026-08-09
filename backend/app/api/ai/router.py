from fastapi import APIRouter, Request

from app.api.deps import CurrentUser, DbSession
from app.schemas.schedule import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    ChatRequest,
    ChatResponse,
    ParsedRoutine,
    ParseRoutineRequest,
)
from app.schemas.conversation import ChatHistoryResponse
from app.schemas.auth import MessageResponse
from app.services.ai.analyze_service import AIAnalyzeService
from app.services.ai.routine_parser import AIRoutineParserService
from app.services.ai.scheduler_agent import AIChatService
from app.services.ai.conversation_service import ConversationService
from app.core.rate_limit import limiter

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/parse-routine", response_model=ParsedRoutine)
@limiter.limit("10/minute")
async def parse_routine(request: Request, data: ParseRoutineRequest, current_user: CurrentUser):
    service = AIRoutineParserService()
    return await service.parse_routine(data)


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, data: ChatRequest, current_user: CurrentUser, db: DbSession):
    service = AIChatService(db=db, user_id=current_user.id)
    return await service.chat(data)


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(current_user: CurrentUser, db: DbSession):
    service = ConversationService(db)
    conv = await service.get_history(current_user.id)
    return conv


@router.delete("/chat/history", response_model=MessageResponse)
async def clear_chat_history(current_user: CurrentUser, db: DbSession):
    service = ConversationService(db)
    await service.clear_history(current_user.id)
    return MessageResponse(message="Chat history cleared")


@router.post("/analyze", response_model=AIAnalyzeResponse)
@limiter.limit("5/minute")
async def analyze(
    request: Request,
    data: AIAnalyzeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    service = AIAnalyzeService(db)
    return await service.analyze(current_user.id, data)
