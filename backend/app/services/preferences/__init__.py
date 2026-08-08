from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserPreferences
from app.repositories.preferences_repository import PreferencesRepository
from app.schemas.preferences import UserPreferencesResponse, UserPreferencesUpdate


class PreferencesService:
    def __init__(self, db: AsyncSession):
        self.repo = PreferencesRepository(db)

    async def get_preferences(self, user_id: UUID) -> UserPreferencesResponse:
        prefs = await self.repo.get_by_user(user_id)
        if not prefs:
            # Create default preferences
            prefs = UserPreferences(user_id=user_id)
            prefs = await self.repo.create(prefs)
        return UserPreferencesResponse.model_validate(prefs)

    async def update_preferences(
        self, user_id: UUID, data: UserPreferencesUpdate
    ) -> UserPreferencesResponse:
        prefs = await self.repo.get_by_user(user_id)
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            prefs = await self.repo.create(prefs)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prefs, field, value)

        prefs = await self.repo.update(prefs)
        return UserPreferencesResponse.model_validate(prefs)

    async def replace_preferences(
        self, user_id: UUID, data: UserPreferencesUpdate
    ) -> UserPreferencesResponse:
        prefs = await self.repo.get_by_user(user_id)
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            prefs = await self.repo.create(prefs)

        # For PUT, apply all fields (including None values)
        update_data = data.model_dump()
        for field, value in update_data.items():
            setattr(prefs, field, value)

        prefs = await self.repo.update(prefs)
        return UserPreferencesResponse.model_validate(prefs)
