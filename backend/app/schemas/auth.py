from datetime import datetime, time
from typing import Any, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

T = TypeVar("T")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str | None = Field(default=None, max_length=255)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class FirebaseAuthRequest(BaseModel):
    id_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)


class DeleteAccountRequest(BaseModel):
    password: str | None = None


class UserProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    age: int | None = Field(default=None, ge=1, le=150)
    occupation: str | None = Field(default=None, max_length=255)
    timezone: str | None = Field(default=None, max_length=64)
    wake_time: time | None = None
    sleep_time: time | None = None
    working_days: list[str] | None = None
    preferred_study_hours: dict[str, Any] | None = None
    reminder_preferences: dict[str, Any] | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    name: str | None = None
    age: int | None = None
    occupation: str | None = None
    timezone: str
    wake_time: time | None = None
    sleep_time: time | None = None
    working_days: list[str] | None = None
    preferred_study_hours: dict[str, Any] | None = None
    reminder_preferences: dict[str, Any] | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class ResetTokenResponse(BaseModel):
    reset_token: str
    message: str = "Password reset token generated"
