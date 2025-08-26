import json

from app.db.repositories.redis.base_redis_repository import BaseRedisRepository


class QuizRedisRepository(BaseRedisRepository):
    def __init__(self, redis):
        super().__init__(redis)

    async def save_answers(
        self, participant_id: str, record_id: str, answers: list[dict]
    ):
        def get_key(answer):
            return f"{participant_id}:{record_id}:{answer['answer_id']}"

        await super().set(data=answers, get_key=get_key, expire=172800)
