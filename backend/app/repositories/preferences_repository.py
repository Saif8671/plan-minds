from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserPreferences
from app.repositories.base import BaseRepository


class PreferencesRepository(BaseRepository[UserPreferences]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserPreferences, db)

    async def get_by_user(self, user_id: UUID) -> UserPreferences | None:
        result = await self.db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        return result.scalar_one_or_none()
