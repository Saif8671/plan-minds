from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.models import User
from app.services.auth.auth_service import AuthService

DbSession = Annotated[AsyncSession, Depends(get_db)]

# HTTPBearer scheme — shows the lock icon in /docs and enables OpenAPI auth UI
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)] = None,
) -> User:
    """Validate the Bearer token and return the authenticated user.

    Raises 401 if the token is missing, malformed, or invalid.
    """
    if not credentials or not credentials.credentials:
        raise UnauthorizedError("Missing or invalid authorization header")

    token = credentials.credentials
    auth_service = AuthService(db)
    return await auth_service.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]
