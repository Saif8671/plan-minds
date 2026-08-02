from typing import Any


class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Any | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message, status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Not enough permissions"):
        super().__init__(message, status_code=403)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class ValidationError(AppException):
    def __init__(self, message: str, details: Any | None = None):
        super().__init__(message, status_code=422, details=details)


class ExternalServiceError(AppException):
    def __init__(self, service: str, message: str = "External service error"):
        super().__init__(f"{service}: {message}", status_code=502)
