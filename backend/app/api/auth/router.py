from fastapi import APIRouter, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import DbSession, _bearer, CurrentUser
from app.schemas.auth import (
    FirebaseAuthRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    VerifyOTPRequest,
    ResetTokenResponse,
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
async def logout(
    db: DbSession,
    user: CurrentUser,
    credentials: HTTPAuthorizationCredentials = Depends(_bearer)
):
    if credentials and credentials.credentials:
        service = AuthService(db)
        await service.logout(credentials.credentials)
    return ApiResponse(data=MessageData(message="Logged out successfully"))


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
@limiter.limit("30/minute")
async def refresh_token(request: Request, data: TokenRefreshRequest, db: DbSession):
    service = AuthService(db)
    result = await service.refresh(data.refresh_token)
    return ApiResponse(data=result)


@router.post("/forgot-password", response_model=ApiResponse[ResetTokenResponse])
@limiter.limit("5/minute")
async def forgot_password(request: Request, data: ForgotPasswordRequest, db: DbSession):
    service = AuthService(db)
    result = await service.forgot_password(data.email)
    return ApiResponse(data=result)


@router.post("/verify-otp", response_model=ApiResponse[ResetTokenResponse])
@limiter.limit("10/minute")
async def verify_otp(request: Request, data: VerifyOTPRequest, db: DbSession):
    service = AuthService(db)
    result = await service.verify_otp(data.email, data.otp)
    return ApiResponse(data=result)


@router.post("/reset-password", response_model=ApiResponse[MessageData])
@limiter.limit("5/minute")
async def reset_password(request: Request, data: ResetPasswordRequest, db: DbSession):
    service = AuthService(db)
    await service.reset_password(data.token, data.password)
    return ApiResponse(data=MessageData(message="Password has been reset successfully"))
