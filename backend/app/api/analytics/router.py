from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.api.deps import CurrentUser, DbSession
from app.schemas.analytics import DashboardAnalytics, PeriodAnalytics
from app.schemas.base import ApiResponse
from app.services.analytics.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=ApiResponse[DashboardAnalytics])
async def get_dashboard(current_user: CurrentUser, db: DbSession):
    service = AnalyticsService(db)
    result = await service.get_dashboard(current_user.id)
    return ApiResponse(data=result)


@router.get("/weekly", response_model=ApiResponse[PeriodAnalytics])
async def get_weekly_analytics(current_user: CurrentUser, db: DbSession):
    service = AnalyticsService(db)
    result = await service.get_weekly(current_user.id)
    return ApiResponse(data=result)


@router.get("/monthly", response_model=ApiResponse[PeriodAnalytics])
async def get_monthly_analytics(current_user: CurrentUser, db: DbSession):
    service = AnalyticsService(db)
    result = await service.get_monthly(current_user.id)
    return ApiResponse(data=result)


@router.get("/reports/weekly", response_class=PlainTextResponse)
async def get_weekly_report(current_user: CurrentUser, db: DbSession):
    service = AnalyticsService(db)
    return await service.generate_weekly_report_markdown(current_user.id)
