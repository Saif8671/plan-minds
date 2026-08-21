import redis.asyncio as redis
import logging
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

redis_client = None

async def init_redis():
    global redis_client
    url = settings.redis_url or "redis://localhost:6379"
    redis_client = redis.from_url(url, decode_responses=True)
    try:
        await redis_client.ping()
        logger.info(f"Connected to Redis at {url}")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

async def get_redis():
    if redis_client is None:
        await init_redis()
    return redis_client
