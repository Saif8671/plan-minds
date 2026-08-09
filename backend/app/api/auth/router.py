from fastapi import APIRouter, Request

from app.api.deps import DbSession
from app.schemas.auth import (
    FirebaseAuthRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schemas.base import ApiResponse, MessageData
from app.services.auth.auth_service import AuthService
from app.core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[TokenResponse], status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, data: UserRegisterRequest, db: DbSession):
    service = AuthService(db)
    result = await service.register(data)
    return ApiResponse(data=result)


@router.post("/login", response_model=ApiResponse[TokenResponse])
@limiter.limit("10/minute")
async def login(request: Request, data: UserLoginRequest, db: DbSession):
    service = AuthService(db)
    result = await service.login(data)
    return ApiResponse(data=result)


@router.post("/firebase", response_model=ApiResponse[TokenResponse])
@limiter.limit("10/minute")
async def firebase_login(request: Request, data: FirebaseAuthRequest, db: DbSession):
    service = AuthService(db)
    result = await service.authenticate_firebase(data)
    return ApiResponse(data=result)


@router.post("/logout", response_model=ApiResponse[MessageData])
async def logout():
    return ApiResponse(data=MessageData(message="Logged out successfully"))


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
@limiter.limit("30/minute")
async def refresh_token(request: Request, data: TokenRefreshRequest, db: DbSession):
    service = AuthService(db)
    result = await service.refresh(data.refresh_token)
    return ApiResponse(data=result)
