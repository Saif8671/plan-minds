from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.gamification import UserStatsResponse, LeaderboardEntry
from app.schemas.base import ApiResponse
from app.services.gamification.xp_service import GamificationService

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/progress", response_model=ApiResponse[UserStatsResponse])
async def get_user_stats(current_user: CurrentUser, db: DbSession):
    service = GamificationService(db)
    stats = await service.get_user_stats(current_user.id)
    xp_to_next = (stats.level ** 2) * 100
    
    result = UserStatsResponse(
        level=stats.level,
        currentXP=stats.xp,
        xpToNextLevel=xp_to_next,
        currentStreak=stats.streak_days,
        longestStreak=stats.streak_days, # Assuming we don't have longestStreak in DB, fallback to current
        productivityScore=85, # Dummy value for now or calculate from tasks
        badges=[], # Empty badges list
        todayProgress=0, # Empty progress
    )
    return ApiResponse(data=result)


@router.get("/leaderboard", response_model=ApiResponse[list[LeaderboardEntry]])
async def get_leaderboard(db: DbSession, limit: int = 10):
    service = GamificationService(db)
    result = await service.get_leaderboard(limit=limit)
    return ApiResponse(data=result)
