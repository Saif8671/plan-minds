from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.preferences import UserPreferencesResponse, UserPreferencesUpdate
from app.services.preferences import PreferencesService

router = APIRouter(prefix="/users/me/preferences", tags=["User Preferences"])


@router.get("", response_model=UserPreferencesResponse)
async def get_preferences(current_user: CurrentUser, db: DbSession):
    service = PreferencesService(db)
    return await service.get_preferences(current_user.id)


@router.put("", response_model=UserPreferencesResponse)
async def replace_preferences(
    data: UserPreferencesUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = PreferencesService(db)
    return await service.replace_preferences(current_user.id, data)


@router.patch("", response_model=UserPreferencesResponse)
async def update_preferences(
    data: UserPreferencesUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = PreferencesService(db)
    return await service.update_preferences(current_user.id, data)
