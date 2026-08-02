from fastapi import APIRouter

from app.api.ai.router import router as ai_router
from app.api.analytics.router import router as analytics_router
from app.api.auth.router import router as auth_router
from app.api.notifications.router import router as notifications_router
from app.api.reminders.router import router as reminders_router
from app.api.schedule.router import router as schedule_router
from app.api.tasks.router import router as tasks_router
from app.api.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(tasks_router)
api_router.include_router(ai_router)
api_router.include_router(schedule_router)
api_router.include_router(reminders_router)
api_router.include_router(analytics_router)
api_router.include_router(notifications_router)
