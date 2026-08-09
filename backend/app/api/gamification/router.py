from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.gamification import UserStatsResponse, LeaderboardEntry
from app.services.gamification.xp_service import GamificationService

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(current_user: CurrentUser, db: DbSession):
    service = GamificationService(db)
    stats = await service.get_user_stats(current_user.id)
    return UserStatsResponse(
        xp=stats.xp,
        level=stats.level,
        streak_days=stats.streak_days,
        last_active_date=stats.last_active_date,
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(db: DbSession, limit: int = 10):
    service = GamificationService(db)
    return await service.get_leaderboard(limit=limit)
