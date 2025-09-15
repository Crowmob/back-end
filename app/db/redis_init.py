import redis.asyncio as redis

from app.utils.settings_model import settings

pool = redis.ConnectionPool(host=settings.redis.HOST, port=settings.redis.PORT)


def get_redis_client():
    return redis.Redis(connection_pool=pool)
