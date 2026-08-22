from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.base import ApiResponse
from app.schemas.gamification import LeaderboardEntry, UserStatsResponse
from app.services.gamification.xp_service import GamificationService

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/progress", response_model=ApiResponse[UserStatsResponse])
async def get_user_stats(current_user: CurrentUser, db: DbSession):
    service = GamificationService(db)
    stats = await service.get_user_stats(current_user.id)
    xp_to_next = (stats.level**2) * 100

    today_progress = await service.get_today_progress(current_user.id)
    productivity_score = await service.get_productivity_score(current_user.id)
    badges = await service.get_badges(stats)

    result = UserStatsResponse(
        level=stats.level,
        currentXP=stats.xp,
        xpToNextLevel=xp_to_next,
        currentStreak=stats.streak_days,
        longestStreak=stats.longest_streak,
        productivityScore=productivity_score,
        badges=badges,
        todayProgress=today_progress,
    )
    return ApiResponse(data=result)


@router.get("/leaderboard", response_model=ApiResponse[list[LeaderboardEntry]])
async def get_leaderboard(db: DbSession, limit: int = 10):
    service = GamificationService(db)
    result = await service.get_leaderboard(limit=limit)
    return ApiResponse(data=result)
