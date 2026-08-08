import json
import logging
from uuid import UUID

from pywebpush import WebPushException, webpush
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
        self, user_id: UUID, endpoint: str, p256dh: str, auth: str
    ) -> PushSubscription:
        # Check if exists
        result = await self.db.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint,
            )
        )
        sub = result.scalars().first()
        if sub:
            sub.p256dh = p256dh
            sub.auth = auth
        else:
            sub = PushSubscription(
                user_id=user_id,
                endpoint=endpoint,
                p256dh=p256dh,
                auth=auth,
            )
            self.db.add(sub)

        await self.db.flush()
        await self.db.refresh(sub)
        return sub

    async def unsubscribe(self, user_id: UUID, endpoint: str) -> None:
        result = await self.db.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint,
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

        payload = json.dumps({"title": title, "body": body, "data": data or {}})

        vapid_key = settings.vapid_private_key
        if not vapid_key:
            logger.debug("VAPID_PRIVATE_KEY is not set. Skipping web push.")
            return

        vapid_claims = {"sub": settings.vapid_email}

        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
            }
            try:
                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=vapid_key,
                    vapid_claims=vapid_claims,
                )
            except WebPushException as ex:
                logger.error("Web push failed: %s", ex)
                # Remove invalid subscriptions (HTTP 410 Gone)
                if ex.response and ex.response.status_code == 410:
                    await self.unsubscribe(user_id, sub.endpoint)
            except Exception as e:
                logger.error("Failed to send push: %s", e)
