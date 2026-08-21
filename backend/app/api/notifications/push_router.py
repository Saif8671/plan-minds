from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.notification import PushSubscriptionCreate, PushSubscriptionResponse
from app.services.notifications.push_service import PushService

router = APIRouter(prefix="/notifications/push", tags=["Push Notifications"])


@router.post("/subscribe", response_model=PushSubscriptionResponse)
async def subscribe(
    data: PushSubscriptionCreate,
    current_user: CurrentUser,
    db: DbSession,
):
    service = PushService(db)
    sub = await service.subscribe(
        user_id=current_user.id,
        push_token=data.push_token,
    )
    return sub


@router.delete("/unsubscribe", status_code=204)
async def unsubscribe(
    push_token: str,
    current_user: CurrentUser,
    db: DbSession,
):
    service = PushService(db)
    await service.unsubscribe(current_user.id, push_token)
