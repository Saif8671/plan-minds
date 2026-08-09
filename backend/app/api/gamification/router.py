from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.gamification import UserStatsResponse, LeaderboardEntry
from app.schemas.base import ApiResponse
from app.services.gamification.xp_service import GamificationService

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/stats", response_model=ApiResponse[UserStatsResponse])
async def get_user_stats(current_user: CurrentUser, db: DbSession):
    service = GamificationService(db)
    stats = await service.get_user_stats(current_user.id)
    result = UserStatsResponse(
        xp=stats.xp,
        level=stats.level,
        streak_days=stats.streak_days,
        last_active_date=stats.last_active_date,
    )
    return ApiResponse(data=result)


@router.get("/leaderboard", response_model=ApiResponse[list[LeaderboardEntry]])
async def get_leaderboard(db: DbSession, limit: int = 10):
    service = GamificationService(db)
    result = await service.get_leaderboard(limit=limit)
    return ApiResponse(data=result)
