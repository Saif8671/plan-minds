from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    current_state: str
    missing_fields: dict[str, Any] | None = None
    updated_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class ChatHistoryResponse(BaseModel):
    conversation: ConversationResponse
    state: ConversationStateResponse | None = None
    messages: list[MessageResponse]
