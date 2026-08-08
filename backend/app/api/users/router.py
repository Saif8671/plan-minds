from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    MessageResponse,
    UserProfileUpdate,
    UserResponse,
)
from app.services.auth.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: CurrentUser, db: DbSession):
    service = UserService(db)
    return await service.get_profile(current_user.id)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = UserService(db)
    return await service.update_profile(current_user.id, data)


@router.patch("/me", response_model=UserResponse)
async def patch_my_profile(
    data: UserProfileUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = UserService(db)
    return await service.update_profile(current_user.id, data)


@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    service = UserService(db)
    await service.change_password(current_user.id, data.old_password, data.new_password)
    return MessageResponse(message="Password changed successfully")


@router.delete("/me", response_model=MessageResponse)
async def delete_account(
    current_user: CurrentUser,
    db: DbSession,
    data: DeleteAccountRequest | None = None,
):
    service = UserService(db)
    password = data.password if data else None
    await service.delete_account(current_user.id, password)
    return MessageResponse(message="Account deleted successfully")
