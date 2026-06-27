import redis
import os
from app.core.config import settings

_redis_client = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        redis_url = settings.REDIS_URL or os.environ.get("REDIS_URL", "redis://localhost:6379")
        try:
            _redis_client = redis.from_url(redis_url, decode_responses=True)
            _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client
