import redis.asyncio as redis

from app.utils.settings_model import settings

pool = redis.ConnectionPool(host=settings.redis.HOST, port=settings.redis.PORT)

redis_client = redis.Redis(connection_pool=pool)
