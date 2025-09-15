from app.db.repositories.redis.base_redis_repository import BaseRedisRepository


class QuizRedisRepository(BaseRedisRepository):
    expire = 172800

    @staticmethod
    def get_key(item: dict):
        return f"{item['user_id']}:{item['quiz_id']}:{item['company_id']}:{item['answer_id']}"

    async def save_answers(self, answers: list[dict]):
        await super().set(data=answers, expire=self.expire)

    async def get_answers_for_user(
        self, user_id: int, quiz_id: int = None, company_id: int = None
    ):
        pattern = f"{user_id}:{quiz_id if quiz_id else '*'}:{company_id if company_id else '*'}:*"
        answers = await super().get_many(pattern=pattern)
        return answers
