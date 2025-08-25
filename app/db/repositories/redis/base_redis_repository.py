import json


class BaseRedisRepository:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def set(self, key: str, value: dict, expire: int = None):
        await self.redis.set(key, json.dumps(value), ex=expire)

    async def get(self, key: str):
        raw = await self.redis.get(key)
        return json.loads(raw) if raw else None

    async def delete(self, key: str):
        await self.redis.delete(key)
