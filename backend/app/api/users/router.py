from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    UserProfileUpdate,
    UserResponse,
)
from app.schemas.base import ApiResponse, MessageData
from app.services.auth.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_my_profile(current_user: CurrentUser, db: DbSession):
    service = UserService(db)
    result = await service.get_profile(current_user.id)
    return ApiResponse(data=result)


@router.put("/me", response_model=ApiResponse[UserResponse])
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = UserService(db)
    result = await service.update_profile(current_user.id, data)
    return ApiResponse(data=result)


@router.patch("/me", response_model=ApiResponse[UserResponse])
async def patch_my_profile(
    data: UserProfileUpdate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = UserService(db)
    result = await service.update_profile(current_user.id, data)
    return ApiResponse(data=result)


@router.put("/me/password", response_model=ApiResponse[MessageData])
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    service = UserService(db)
    await service.change_password(current_user.id, data.old_password, data.new_password)
    return ApiResponse(data=MessageData(message="Password changed successfully"))


@router.delete("/me", response_model=ApiResponse[MessageData])
async def delete_account(
    current_user: CurrentUser,
    db: DbSession,
    data: DeleteAccountRequest | None = None,
):
    service = UserService(db)
    password = data.password if data else None
    await service.delete_account(current_user.id, password)
    return ApiResponse(data=MessageData(message="Account deleted successfully"))
