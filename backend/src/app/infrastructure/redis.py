# app/infrastructure/redis.py
import redis.asyncio as redis
from typing import Optional

_redis_client: Optional[redis.Redis] = None


async def init_redis(host="127.0.0.1", port=6379, db=0, password=None):
    global _redis_client
    _redis_client = redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True
    )
    await _redis_client.ping()


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        raise RuntimeError("Redis not initialized, call init_redis first")
    return _redis_client
