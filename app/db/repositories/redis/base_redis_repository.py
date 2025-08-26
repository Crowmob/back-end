import json

from typing import Callable
from redis.asyncio import Redis


class BaseRedisRepository:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def set(self, get_key: Callable[[dict], str], data: list[dict], expire: int):
        pipe = self.redis.pipeline()
        for i in data:
            key = get_key(i)
            await pipe.set(key, json.dumps(i), ex=expire)
        await pipe.execute()
