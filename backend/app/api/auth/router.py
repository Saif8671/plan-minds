from fastapi import APIRouter

from app.api.deps import DbSession
from app.schemas.auth import (
    FirebaseAuthRequest,
    MessageResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegisterRequest, db: DbSession):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest, db: DbSession):
    service = AuthService(db)
    return await service.login(data)


@router.post("/firebase", response_model=TokenResponse)
async def firebase_login(data: FirebaseAuthRequest, db: DbSession):
    service = AuthService(db)
    return await service.authenticate_firebase(data)


@router.post("/logout", response_model=MessageResponse)
async def logout():
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefreshRequest, db: DbSession):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)
