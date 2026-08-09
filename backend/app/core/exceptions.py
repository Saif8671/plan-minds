from typing import Any


class AppException(Exception):
    """Base application exception with standardised error envelope."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "APP_ERROR",
        details: Any | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details,
        }


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            f"{resource} not found",
            status_code=404,
            code="NOT_FOUND",
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message, status_code=401, code="UNAUTHORIZED")


class ForbiddenError(AppException):
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message, status_code=403, code="FORBIDDEN")


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409, code="CONFLICT")


class ValidationError(AppException):
    def __init__(self, message: str, details: Any | None = None):
        super().__init__(message, status_code=422, code="VALIDATION_ERROR", details=details)


class ExternalServiceError(AppException):
    def __init__(self, service: str, message: str = "External service error"):
        super().__init__(
            f"{service}: {message}",
            status_code=502,
            code="EXTERNAL_SERVICE_ERROR",
        )


class ScheduleConflictError(AppException):
    """Raised when a schedule operation would create time conflicts."""

    def __init__(self, conflicts: list[dict]):
        super().__init__(
            "Schedule conflicts detected",
            status_code=409,
            code="SCHEDULE_CONFLICT",
            details={"conflicts": conflicts},
        )


class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429, code="RATE_LIMIT_EXCEEDED")
