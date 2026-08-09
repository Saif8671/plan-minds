from datetime import date
from pydantic import BaseModel

class UserStatsResponse(BaseModel):
    xp: int
    level: int
    streak_days: int
    last_active_date: date | None = None

class LeaderboardEntry(BaseModel):
    user_id: str
    name: str | None = None
    level: int
    xp: int
