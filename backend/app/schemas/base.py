from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiError(BaseModel):
    message: str = Field(..., description="A human-readable error message.")
    code: str = Field(..., description="A unique string code for the error type.")
    details: Any | None = Field(
        default=None, description="Optional details about the error."
    )


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = Field(default=None, description="The response data payload.")
    error: ApiError | None = Field(
        default=None, description="Error information, if any."
    )


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class MessageData(BaseModel):
    message: str
