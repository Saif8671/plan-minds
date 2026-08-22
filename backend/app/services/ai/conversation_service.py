import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Conversation, ConversationMessage, ConversationState


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_active_conversation(
        self, user_id: uuid.UUID
    ) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .where(Conversation.status == "active")
            .options(
                selectinload(Conversation.messages),
                selectinload(Conversation.state),
            )
            .order_by(Conversation.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        conv = result.scalar_one_or_none()

        if not conv:
            conv = Conversation(user_id=user_id, title="Chat Session")
            state = ConversationState(
                conversation=conv, current_state="DEFAULT", missing_fields={}
            )
            self.db.add(conv)
            self.db.add(state)
            await self.db.commit()
            await self.db.refresh(conv)

        return conv

    async def get_history(self, user_id: uuid.UUID) -> Conversation:
        conv = await self.get_or_create_active_conversation(user_id)
        return conv

    async def clear_history(self, user_id: uuid.UUID) -> None:
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .where(Conversation.status == "active")
        )
        result = await self.db.execute(stmt)
        convs = result.scalars().all()
        for c in convs:
            c.status = "archived"
        await self.db.commit()

    async def add_message(
        self, conversation_id: uuid.UUID, role: str, content: str
    ) -> ConversationMessage:
        msg = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def update_state(
        self, conversation_id: uuid.UUID, current_state: str, missing_fields: dict
    ) -> ConversationState:
        stmt = select(ConversationState).where(
            ConversationState.conversation_id == conversation_id
        )
        result = await self.db.execute(stmt)
        state = result.scalar_one_or_none()
        if not state:
            state = ConversationState(
                conversation_id=conversation_id,
                current_state=current_state,
                missing_fields=missing_fields,
            )
            self.db.add(state)
        else:
            state.current_state = current_state
            state.missing_fields = missing_fields
        await self.db.commit()
        await self.db.refresh(state)
        return state
