from uuid import UUID

from cachetools import TTLCache
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories.base import BaseRepository

_user_cache = TTLCache(maxsize=100, ttl=300)


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_google_sub(self, google_sub: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.google_sub == google_sub)
        )
        return result.scalar_one_or_none()

    async def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.firebase_uid == firebase_uid)
        )
        return result.scalar_one_or_none()

    async def get_active_by_id(self, user_id: UUID) -> User | None:
        cache_key = f"active_{user_id}"
        if cache_key in _user_cache:
            return _user_cache[cache_key]

        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_active.is_(True))
        )
        user = result.scalar_one_or_none()
        if user:
            _user_cache[cache_key] = user
        return user

    async def get_by_id(self, id: UUID) -> User | None:
        cache_key = f"user_{id}"
        if cache_key in _user_cache:
            return _user_cache[cache_key]

        user = await super().get_by_id(id)
        if user:
            _user_cache[cache_key] = user
        return user
