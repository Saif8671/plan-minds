from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.models import User
from app.services.auth.auth_service import AuthService

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid authorization header")

    token = authorization.removeprefix("Bearer ").strip()
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]
