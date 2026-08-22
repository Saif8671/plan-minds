import time as _time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logger import get_logger, new_request_id, setup_logging
from app.core.scheduler import start_scheduler, stop_scheduler

settings = get_settings()
logger = get_logger(__name__)

# ─── OpenAPI tags metadata ──────────────────────────────────────────────

TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "Register, login (email/password + Firebase), token refresh",
    },
    {"name": "Users", "description": "User profile management and account operations"},
    {
        "name": "Preferences",
        "description": "Scheduling preferences, work hours, notification settings",
    },
    {
        "name": "Tasks",
        "description": "Create, list, update, complete, skip, and delete tasks",
    },
    {
        "name": "Schedules",
        "description": "AI-generated daily schedules, block editing, validation",
    },
    {
        "name": "Routines",
        "description": "Store and manage recurring routine descriptions",
    },
    {
        "name": "Reminders",
        "description": "One-time and recurring reminders with history",
    },
    {
        "name": "Notifications",
        "description": "In-app notification inbox and push subscription management",
    },
    {"name": "Push", "description": "Web Push subscription management (VAPID)"},
    {
        "name": "AI",
        "description": "Natural language routine parsing, schedule analysis, and AI chat assistant",
    },
    {
        "name": "Analytics",
        "description": "Task completion analytics, focus hours, weekly/monthly reports",
    },
    {
        "name": "Gamification",
        "description": "XP awards, level progression, streak tracking, leaderboard",
    },
    {"name": "Health", "description": "Service health and readiness checks"},
]


# ─── Lifespan ───────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    if settings.run_scheduler:
        start_scheduler()
    yield
    if settings.run_scheduler:
        stop_scheduler()
    logger.info("Shutting down %s", settings.app_name)


# ─── App factory ────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "**PlanMinds** — AI-powered schedule organiser backend API.\n\n"
        "All protected endpoints require `Authorization: Bearer <access_token>`."
    ),
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─── Rate limiter ───────────────────────────────────────────────────────

from app.core.rate_limit import limiter  # noqa: E402

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── CORS ───────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request logging middleware ─────────────────────────────────────────


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    rid = new_request_id()
    request.state.request_id = rid
    start = _time.monotonic()
    response = await call_next(request)
    duration_ms = round((_time.monotonic() - start) * 1000, 1)
    logger.info(
        "%s %s → %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={"request_id": rid, "path": request.url.path, "method": request.method},
    )
    response.headers["X-Request-ID"] = rid
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    return response


# ─── Exception handlers ─────────────────────────────────────────────────


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    from app.schemas.base import ApiError, ApiResponse

    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            error=ApiError(
                message=exc.message,
                code=exc.code,
                details=exc.details,
            )
        ).model_dump(mode="json", exclude_none=True),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    from app.schemas.base import ApiError, ApiResponse

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ApiResponse(
            error=ApiError(
                message="Request validation failed",
                code="VALIDATION_ERROR",
                details=exc.errors(),
            )
        ).model_dump(mode="json", exclude_none=True),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    from app.schemas.base import ApiError, ApiResponse

    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            error=ApiError(
                message="Internal server error",
                code="INTERNAL_ERROR",
            )
        ).model_dump(mode="json", exclude_none=True),
    )


# ─── Health endpoints ────────────────────────────────────────────────────


@app.get("/health", tags=["Health"], summary="Basic health check")
async def health_check():
    """Returns 200 OK when the server is running."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health/detailed", tags=["Health"], summary="Detailed readiness check")
async def health_detailed():
    """Checks database connectivity and scheduler status."""
    from app.core.database import engine
    from app.core.scheduler import scheduler

    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "scheduler": "running" if scheduler.running else "stopped",
        "ai_key_configured": bool(settings.groq_api_key),
        "vapid_configured": bool(settings.vapid_private_key),
    }


# ─── Include routers ─────────────────────────────────────────────────────

app.include_router(api_router, prefix=settings.api_v1_prefix)
