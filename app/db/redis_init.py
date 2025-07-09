from redis.asyncio import Redis
from app.core.settings_model import settings

redis_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
