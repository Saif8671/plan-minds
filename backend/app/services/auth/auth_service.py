from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.firebase import verify_firebase_id_token
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_password_reset_token,
    verify_token,
)
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    FirebaseAuthRequest,
    ResetTokenResponse,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegisterRequest) -> TokenResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            firebase_uid=None,
            google_sub=None,
            name=data.name,
        )
        user = await self.user_repo.create(user)

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if (
            not user
            or not user.hashed_password
            or not verify_password(data.password, user.hashed_password)
        ):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def authenticate_firebase(self, data: FirebaseAuthRequest) -> TokenResponse:
        try:
            payload = verify_firebase_id_token(data.id_token)
        except Exception as exc:
            raise UnauthorizedError("Invalid Firebase credential") from exc

        firebase_uid = payload.get("uid")
        email = payload.get("email")
        name = payload.get("name")

        if not firebase_uid or not email:
            raise UnauthorizedError("Firebase account information is incomplete")

        user = await self.user_repo.get_by_firebase_uid(firebase_uid)
        if user:
            if not user.is_active:
                raise UnauthorizedError("Account is deactivated")
            return TokenResponse(
                access_token=create_access_token(user.id),
                refresh_token=create_refresh_token(user.id),
            )

        user = await self.user_repo.get_by_email(email)
        if user:
            if not user.is_active:
                raise UnauthorizedError("Account is deactivated")
            if user.firebase_uid and user.firebase_uid != firebase_uid:
                raise UnauthorizedError(
                    "Firebase account already linked to another user"
                )
            user.firebase_uid = firebase_uid
            if not user.name and name:
                user.name = name
            await self.user_repo.update(user)
        else:
            user = User(
                email=email,
                hashed_password=None,
                firebase_uid=firebase_uid,
                google_sub=None,
                name=name,
            )
            user = await self.user_repo.create(user)

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        user_id = verify_token(refresh_token, expected_type="refresh")
        if not user_id:
            raise UnauthorizedError("Invalid refresh token")

        user = await self.user_repo.get_active_by_id(UUID(user_id))
        if not user:
            raise UnauthorizedError("User not found or inactive")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def get_current_user(self, token: str) -> User:
        user_id = verify_token(token, expected_type="access")
        if not user_id:
            raise UnauthorizedError()

        user = await self.user_repo.get_active_by_id(UUID(user_id))
        if not user:
            raise UnauthorizedError("User not found or inactive")
        return user

    # ─── Password reset flow ───────────────────────────────────────────

    async def forgot_password(self, email: str) -> ResetTokenResponse:
        """Generate a password-reset token for the given email.

        In dev mode the token is returned directly in the response.
        In production you would send it via email instead.
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Don't reveal whether the email exists — return a generic response
            return ResetTokenResponse(
                reset_token="",
                message="If an account with that email exists, a reset link has been sent.",
            )
        token = create_password_reset_token(user.id)
        return ResetTokenResponse(
            reset_token=token,
            message="If an account with that email exists, a reset link has been sent.",
        )

    async def verify_otp(self, email: str, otp: str) -> ResetTokenResponse:
        """Verify a reset token / OTP and issue a fresh reset token for the final step.

        Currently the OTP *is* the JWT token. In production you would
        verify a 6-digit code stored in cache/DB.
        """
        user_id = verify_password_reset_token(otp)
        if not user_id:
            raise UnauthorizedError("Invalid or expired OTP")

        user = await self.user_repo.get_active_by_id(UUID(user_id))
        if not user or user.email != email:
            raise UnauthorizedError("Invalid or expired OTP")

        # Issue a fresh short-lived token for the reset step
        fresh_token = create_password_reset_token(user.id)
        return ResetTokenResponse(reset_token=fresh_token, message="OTP verified")

    async def reset_password(self, token: str, new_password: str) -> None:
        """Consume a valid reset token and set a new password."""
        user_id = verify_password_reset_token(token)
        if not user_id:
            raise UnauthorizedError("Invalid or expired reset token")

        user = await self.user_repo.get_active_by_id(UUID(user_id))
        if not user:
            raise NotFoundError("User")

        user.hashed_password = hash_password(new_password)
        await self.user_repo.update(user)
