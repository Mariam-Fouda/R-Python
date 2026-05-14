import redis
import json
from typing import Optional, Any
from app.core.config import settings
from app.core.logger import logger

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

DEFAULT_TTL = 300  # 5 minutes


def get_cache(key: str) -> Optional[Any]:
    try:
        data = redis_client.get(key)
        if data:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(data)
        logger.debug(f"Cache MISS: {key}")
        return None
    except Exception as e:
        logger.warning(f"Redis get error: {e}")
        return None


def set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL):
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        logger.debug(f"Cache SET: {key} (TTL={ttl}s)")
    except Exception as e:
        logger.warning(f"Redis set error: {e}")


def delete_cache(key: str):
    try:
        redis_client.delete(key)
        logger.debug(f"Cache DELETE: {key}")
    except Exception as e:
        logger.warning(f"Redis delete error: {e}")


def delete_pattern(pattern: str):
    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
            logger.debug(f"Cache DELETE pattern: {pattern} ({len(keys)} keys)")
    except Exception as e:
        logger.warning(f"Redis delete pattern error: {e}")


def get_redis_info() -> dict:
    try:
        info = redis_client.info()
        return {
            "connected": True,
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
