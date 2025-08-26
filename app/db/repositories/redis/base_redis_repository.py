import json


class BaseRedisRepository:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def set(self, get_key, data: list[dict], expire: int):
        pipe = self.redis.pipeline()
        for i in data:
            key = get_key(i)
            pipe.set(key, json.dumps(i), ex=expire)
        await pipe.execute()
