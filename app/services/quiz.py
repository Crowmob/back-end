import csv
import datetime
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.quiz_exceptions import NotFoundByIdException
from app.db.redis_init import get_redis_client
from app.db.repositories.redis.quiz_redis_repository import QuizRedisRepository
from app.db.unit_of_work import UnitOfWork
from app.schemas.quiz import (
    QuizWithQuestionsSchema,
    QuestionCreateSchema,
    QuizCreateSchema,
    AnswerCreateSchema,
    QuizUpdateSchema,
    QuizParticipantCreateSchema,
    RecordCreateSchema,
    QuizParticipantUpdateSchema,
    QuizSubmitRequest,
)

logger = logging.getLogger(__name__)


class QuizServices:
    @staticmethod
    async def create_quiz(
        company_id: int, quiz_id: int | None, quiz: QuizWithQuestionsSchema
    ):
        async with UnitOfWork() as uow:
            try:
                if quiz_id is not None:
                    await uow.quizzes.delete(quiz_id)
                quiz_id = await uow.quizzes.create(
                    QuizCreateSchema(
                        title=quiz.title,
                        description=quiz.description,
                        company_id=company_id,
                        frequency=quiz.frequency,
                    ).model_dump()
                )

                questions_data = [
                    QuestionCreateSchema(
                        text=question.text,
                        quiz_id=quiz_id,
                    ).model_dump()
                    for question in quiz.questions
                ]
                question_ids = await uow.questions.create_many(questions_data)

                answers_data = []
                for question, question_id in zip(quiz.questions, question_ids):
                    for answer in question.answers:
                        answers_data.append(
                            AnswerCreateSchema(
                                text=answer.text,
                                is_correct=answer.is_correct,
                                question_id=question_id,
                            ).model_dump()
                        )
                await uow.answers.create_many(answers_data)

                logger.info(f"Created quiz id: {quiz_id}")
                return quiz_id

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_quiz_by_id(quiz_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                return await uow.quizzes.get_quiz_by_id(quiz_id, company_id)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_all_quizzes(
        company_id: int,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                return await uow.quizzes.get_all_quizzes(
                    company_id, user_id, limit, offset
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def update_quiz(
        quiz_id: int, title: str | None = None, description: str | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.quizzes.get_by_id(quiz_id)
                if not quiz:
                    raise NotFoundByIdException(
                        detail=f"Quiz with ID {quiz_id} not found"
                    )
                update_model = QuizUpdateSchema(
                    title=title,
                    description=description,
                )
                await uow.quizzes.update(quiz_id, update_model.model_dump())
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def delete_quiz(quiz_id):
        async with UnitOfWork() as uow:
            try:
                await uow.quizzes.delete(quiz_id)
                logger.info(f"Deleted quiz id: {quiz_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def quiz_submit(data: QuizSubmitRequest):
        async with UnitOfWork() as uow:
            try:
                participant = await uow.participants.get_quiz_participant(
                    data.quiz_id, data.user_id
                )
                if not participant:
                    participant_id = await uow.participants.create(
                        QuizParticipantCreateSchema(
                            quiz_id=data.quiz_id, user_id=data.user_id
                        ).model_dump()
                    )
                    logger.info(f"Created quiz participant")
                else:
                    participant_id = participant.id
                    await uow.participants.update(
                        participant_id,
                        QuizParticipantUpdateSchema(
                            completed_at=datetime.datetime.now()
                        ).model_dump(),
                    )
                record_id = await uow.records.create(
                    RecordCreateSchema(
                        participant_id=participant_id, score=data.score
                    ).model_dump()
                )
                selected_answers = [
                    answer.id
                    for question in data.questions
                    for answer in question.answers
                ]
                answer_ids = await uow.answers.create_selected_answers(
                    record_id, selected_answers
                )

                quiz_redis_repo = QuizRedisRepository(get_redis_client())
                answers_data = [
                    {
                        "quiz_id": data.quiz_id,
                        "company_id": data.company_id,
                        "answer_id": answer_id,
                        "participant_id": participant_id,
                        "user_id": data.user_id,
                        "record_id": record_id,
                    }
                    for answer_id in answer_ids
                ]

                await quiz_redis_repo.save_answers(answers_data)

                return participant_id, record_id, answer_ids
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_average_score_in_company(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                score = await uow.records.get_average_score_in_company(
                    user_id, company_id
                )
                return score
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_average_score_in_system(user_id: int):
        async with UnitOfWork() as uow:
            try:
                score = await uow.records.get_average_score_in_system(user_id)
                return score
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_quiz_data_for_user(
        user_id: int, quiz_id: int = None, company_id: int = None
    ):
        async with UnitOfWork() as uow:
            try:
                quiz_redis_repo = QuizRedisRepository(get_redis_client())
                answers = await quiz_redis_repo.get_answers_for_user(
                    user_id, quiz_id, company_id
                )

                answer_ids = [answer["answer_id"] for answer in answers]
                answers = list(answers)

                missing_answers = await uow.answers.get_missing_answers(
                    answer_ids, user_id, quiz_id, company_id
                )
                answers.extend(
                    [
                        {
                            "answer_id": answer.id,
                        }
                        for answer in missing_answers
                    ]
                )

                quiz_data = await uow.quizzes.get_full_quiz_data_for_user(
                    [answer["answer_id"] for answer in answers]
                )
                logger.info(quiz_data)
                return quiz_data
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise


quiz_services = QuizServices()
