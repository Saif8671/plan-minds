from fastapi import APIRouter, Request

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
from app.core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
async def register(request: Request, data: UserRegisterRequest, db: DbSession):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(request: Request, data: UserLoginRequest, db: DbSession):
    service = AuthService(db)
    return await service.login(data)


@router.post("/firebase", response_model=TokenResponse)
@limiter.limit("10/minute")
async def firebase_login(request: Request, data: FirebaseAuthRequest, db: DbSession):
    service = AuthService(db)
    return await service.authenticate_firebase(data)


@router.post("/logout", response_model=MessageResponse)
async def logout():
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh_token(request: Request, data: TokenRefreshRequest, db: DbSession):
    service = AuthService(db)
    return await service.refresh(data.refresh_token)
