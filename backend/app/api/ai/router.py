from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.schedule import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    ChatRequest,
    ChatResponse,
    ParsedRoutine,
    ParseRoutineRequest,
)
from app.services.ai.analyze_service import AIAnalyzeService
from app.services.ai.routine_parser import AIRoutineParserService
from app.services.ai.scheduler_agent import AIChatService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/parse-routine", response_model=ParsedRoutine)
async def parse_routine(data: ParseRoutineRequest, current_user: CurrentUser):
    service = AIRoutineParserService()
    return await service.parse_routine(data)


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest, current_user: CurrentUser, db: DbSession):
    service = AIChatService(db=db, user_id=current_user.id)
    return await service.chat(data)


@router.post("/analyze", response_model=AIAnalyzeResponse)
async def analyze(
    data: AIAnalyzeRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    service = AIAnalyzeService(db)
    return await service.analyze(current_user.id, data)
