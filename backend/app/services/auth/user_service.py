from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserProfileUpdate, UserResponse


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def get_profile(self, user_id: UUID) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        return UserResponse.model_validate(user)

    async def update_profile(
        self, user_id: UUID, data: UserProfileUpdate
    ) -> UserResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user = await self.user_repo.update(user)
        return UserResponse.model_validate(user)

    async def change_password(
        self, user_id: UUID, old_password: str, new_password: str
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        if not user.hashed_password:
            raise UnauthorizedError("This account does not have a password set")

        if not verify_password(old_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")

        user.hashed_password = hash_password(new_password)
        await self.user_repo.update(user)

    async def delete_account(self, user_id: UUID, password: str | None = None) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        # Firebase-only users don't have passwords — allow deletion without one
        if user.hashed_password:
            if not password:
                raise UnauthorizedError("Password is required")
            if not verify_password(password, user.hashed_password):
                raise UnauthorizedError("Password is incorrect")

        await self.user_repo.delete(user)
