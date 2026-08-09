from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserPreferences
from app.repositories.base import BaseRepository
from cachetools import TTLCache

_prefs_cache = TTLCache(maxsize=100, ttl=300)


class PreferencesRepository(BaseRepository[UserPreferences]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserPreferences, db)

    async def get_by_user(self, user_id: UUID) -> UserPreferences | None:
        cache_key = f"prefs_{user_id}"
        if cache_key in _prefs_cache:
            return _prefs_cache[cache_key]
            
        result = await self.db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalar_one_or_none()
        if prefs:
            _prefs_cache[cache_key] = prefs
        return prefs
