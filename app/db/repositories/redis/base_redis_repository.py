import json
from abc import ABC, abstractmethod

from redis.asyncio import Redis


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
