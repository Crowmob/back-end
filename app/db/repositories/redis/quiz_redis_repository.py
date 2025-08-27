from app.db.repositories.redis.base_redis_repository import BaseRedisRepository


class QuizRedisRepository(BaseRedisRepository):
    expire = 172800

    @staticmethod
    def get_key(item: dict):
        return f"{item['participant_id']}:{item['record_id']}:{item['answer_id']}"

    async def save_answers(self, answers: list[dict]):
        await super().set(data=answers, expire=self.expire)
