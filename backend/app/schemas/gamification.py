from datetime import date
from pydantic import BaseModel

class UserStatsResponse(BaseModel):
    level: int
    currentXP: int
    xpToNextLevel: int
    currentStreak: int
    longestStreak: int
    productivityScore: int
    badges: list[dict]
    todayProgress: int

class LeaderboardEntry(BaseModel):
    user_id: str
    name: str | None = None
    level: int
    xp: int

