import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import ConversationMessage, Conversation

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ConversationMessage)
            .join(Conversation)
            .order_by(ConversationMessage.created_at.desc())
            .limit(10)
        )
        messages = result.scalars().all()
        for m in reversed(messages):
            print(f"[{m.created_at}] {m.role}: {m.content}")

if __name__ == "__main__":
    asyncio.run(main())
