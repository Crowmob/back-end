import json
import logging

from redis import RedisError
from redis.asyncio import Redis
from abc import ABC, abstractmethod

from app.core.exceptions.exceptions import AppException

logger = logging.getLogger(__name__)


class BaseRedisRepository(ABC):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    @staticmethod
    @abstractmethod
    def get_key(item: dict):
        pass

    async def set(self, data: list[dict], expire: int):
        try:
            pipe = self.redis.pipeline()
            for i in data:
                key = self.get_key(i)
                await pipe.set(key, json.dumps(i), ex=expire)
            await pipe.execute()
        except RedisError as e:
            logger.error(f"Redis error while setting keys: {e}")
            raise AppException("Cache operation failed")

    async def get_many(self, pattern: str):
        keys = []
        cursor = b"0"

        while cursor:
            try:
                cursor, found_keys = await self.redis.scan(cursor=cursor, match=pattern)
            except RedisError as e:
                logger.error(f"Redis scan failed for pattern {pattern}: {e}")
                raise AppException("Cache scan operation failed")
            keys.extend(found_keys)
            logger.info(cursor)
            if cursor == 0 or cursor == b"0":
                break

        if not keys:
            return []
        try:
            values = await self.redis.mget(*keys)
        except RedisError as e:
            logger.error(f"Redis mget failed for keys {keys}: {e}")
            raise AppException("Cache get operation failed")

        items = [json.loads(v.decode()) for v in values if v is not None]
        return items
