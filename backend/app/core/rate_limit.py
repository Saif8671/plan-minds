from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()
storage_uri = settings.redis_url or "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=storage_uri,
    swallow_errors=True,
    in_memory_fallback_enabled=True,
)
