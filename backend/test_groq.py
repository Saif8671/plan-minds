import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import ConversationMessage, Conversation
from app.services.ai.scheduler_agent import TOOLS, AISchedulerAgent
from app.core.config import get_settings
from groq import AsyncGroq

async def main():
    settings = get_settings()
    client = AsyncGroq(api_key=settings.groq_api_key)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ConversationMessage)
            .join(Conversation)
            .order_by(ConversationMessage.created_at.desc())
            .limit(10)
        )
        db_messages = reversed(result.scalars().all())
        
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        for m in db_messages:
            messages.append({"role": m.role, "content": m.content})
            
    print("Sending messages to Groq:")
    import json
    print(json.dumps(messages, indent=2))
            
    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=1024,
        )
        print("Success:", response)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
