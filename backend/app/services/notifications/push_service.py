import json
import logging
from uuid import UUID

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushServerError,
    PushTicketError,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import PushSubscription

logger = logging.getLogger(__name__)
settings = get_settings()


class PushService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def subscribe(
        self, user_id: UUID, push_token: str
    ) -> PushSubscription:
        # Check if exists
        result = await self.db.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.push_token == push_token,
            )
        )
        sub = result.scalars().first()
        if not sub:
            sub = PushSubscription(
                user_id=user_id,
                push_token=push_token,
            )
            self.db.add(sub)
            await self.db.flush()
            await self.db.refresh(sub)
        return sub

    async def unsubscribe(self, user_id: UUID, push_token: str) -> None:
        result = await self.db.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.push_token == push_token,
            )
        )
        sub = result.scalars().first()
        if sub:
            await self.db.delete(sub)
            await self.db.flush()

    async def send_push_notification(
        self, user_id: UUID, title: str, body: str, data: dict | None = None
    ) -> None:
        result = await self.db.execute(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        )
        subscriptions = result.scalars().all()

        if not subscriptions:
            return

        for sub in subscriptions:
            try:
                response = PushClient().publish(
                    PushMessage(
                        to=sub.push_token,
                        title=title,
                        body=body,
                        data=data or {},
                    )
                )
            except PushServerError as exc:
                logger.error(f"Expo server error for token {sub.push_token}: {exc}")
            except (PushTicketError, DeviceNotRegisteredError) as exc:
                logger.warning(
                    f"Invalid Expo push token {sub.push_token}, unsubscribing: {exc}"
                )
                await self.unsubscribe(user_id, sub.push_token)
            except Exception as exc:
                logger.error(f"Failed to send Expo push to {sub.push_token}: {exc}")
