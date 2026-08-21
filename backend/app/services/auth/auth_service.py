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
from app.models import User, RevokedToken
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
        self.db = db
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
        # Check if token is revoked
        from sqlalchemy import select
        revoked = await self.db.execute(select(RevokedToken).where(RevokedToken.token == token))
        if revoked.scalar_one_or_none():
            raise UnauthorizedError("Token has been revoked")
            
        user_id = verify_token(token, expected_type="access")
        if not user_id:
            raise UnauthorizedError()

        user = await self.user_repo.get_active_by_id(UUID(user_id))
        if not user:
            raise UnauthorizedError("User not found or inactive")
        return user

    async def logout(self, token: str) -> None:
        """Revoke the given access token by adding it to the blacklist."""
        try:
            revoked = RevokedToken(token=token)
            self.db.add(revoked)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            import logging
            logging.error(f"Failed to revoke token: {e}")

    # ─── Password reset flow ───────────────────────────────────────────

    async def forgot_password(self, email: str) -> ResetTokenResponse:
        """Generate a password-reset OTP for the given email.

        In dev mode the OTP is logged to console.
        In production you would send it via email.
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            return ResetTokenResponse(
                reset_token="",
                message="If an account with that email exists, a reset link has been sent.",
            )
            
        import random
        from datetime import UTC, datetime, timedelta
        from app.core.config import get_settings
        from app.services.email_service import EmailService
        
        # 1-minute cooldown per email
        if user.reset_otp_expires_at:
            expires_at = user.reset_otp_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)
            time_since_last_otp = (expires_at - timedelta(minutes=15))
            if (datetime.now(UTC) - time_since_last_otp).total_seconds() < 60:
                # Still in cooldown, just return success without sending
                return ResetTokenResponse(
                    reset_token="",
                    message="If an account with that email exists, a reset link has been sent.",
                )
        
        settings = get_settings()
        otp = f"{random.randint(0, 999999):06d}"
        
        user.reset_otp = otp
        user.reset_otp_expires_at = datetime.now(UTC) + timedelta(minutes=15)
        await self.user_repo.update(user)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Password reset OTP for {email}: {otp}")
        
        await EmailService.send_email(
            to_email=email,
            subject="Your Password Reset Code",
            body=f"Your password reset code is: {otp}. It expires in 15 minutes."
        )
        
        # Security bypass ONLY in development
        if settings.environment == "development":
            return ResetTokenResponse(
                reset_token=otp,
                message="If an account with that email exists, a reset link has been sent.",
            )
            
        return ResetTokenResponse(
            reset_token="",
            message="If an account with that email exists, a reset link has been sent.",
        )

    async def verify_otp(self, email: str, otp: str) -> ResetTokenResponse:
        """Verify a reset OTP and issue a fresh JWT reset token for the final step."""
        user = await self.user_repo.get_by_email(email)
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid or expired OTP")
            
        from datetime import UTC, datetime
        
        if not user.reset_otp or user.reset_otp != otp:
            raise UnauthorizedError("Invalid or expired OTP")
            
        expires_at = user.reset_otp_expires_at
        if expires_at and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
            
        if not expires_at or expires_at < datetime.now(UTC):
            raise UnauthorizedError("Invalid or expired OTP")
            
        # Clear the OTP
        user.reset_otp = None
        user.reset_otp_expires_at = None
        await self.user_repo.update(user)

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
