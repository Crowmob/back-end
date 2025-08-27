import json

from redis.asyncio import Redis
from abc import ABC, abstractmethod


class BaseRedisRepository(ABC):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    @staticmethod
    @abstractmethod
    def get_key(item: dict):
        pass

    async def set(self, data: list[dict], expire: int):
        pipe = self.redis.pipeline()
        for i in data:
            key = self.get_key(i)
            await pipe.set(key, json.dumps(i), ex=expire)
        await pipe.execute()

    async def get_many(self, pattern: str):
        keys = []
        cursor = b"0"

        while cursor:
            cursor, found_keys = await self.redis.scan(cursor=cursor, match=pattern)
            keys.extend(found_keys)
            if cursor == 0 or cursor == b"0":
                break

        if not keys:
            return []

        values = await self.redis.mget(*keys)

        items = [json.loads(v.decode()) for v in values if v is not None]
        return items
