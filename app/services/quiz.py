import datetime
import logging
from sqlite3 import IntegrityError, DataError

from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from app.core.enums.enums import RoleEnum, QuizActions, NotificationStatus
from app.core.exceptions.exceptions import (
    AppException,
    NotFoundException,
    BadRequestException,
    ForbiddenException,
)
from app.core.exceptions.repository_exceptions import (
    RepositoryIntegrityError,
    RepositoryDataError,
    RepositoryDatabaseError,
    RedisRepositoryScanError,
    RedisRepositoryMultipleFetchError,
    RedisRepositoryError,
)
from app.db.redis_init import get_redis_client
from app.db.repositories.redis.quiz_redis_repository import QuizRedisRepository
from app.db.unit_of_work import UnitOfWork
from app.models.quiz_model import SelectedAnswers
from app.schemas.notification import NotificationSchema
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
    QuizWithQuestionsDetailResponse,
    QuestionWithAnswersDetailResponse,
    AnswerDetailResponse,
    QuizDetailResponse,
    QuizParticipantDetailResponse,
    QuizAverageResponse,
    QuizScoreItem,
    UpdatedQuestionSchema,
    UpdatedAnswerSchema,
)
from app.schemas.response_models import ListResponse
from app.websocket.manager import get_manager

logger = logging.getLogger(__name__)


class QuizServices:
    @staticmethod
    async def create_quiz(company_id: int, quiz: QuizWithQuestionsSchema):
        async with UnitOfWork() as uow:
            try:
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

                company = await uow.companies.get_one(id=company_id)
                message = f"New test with name {quiz.title} has been added to company {company.name}"
                await uow.notifications.create(
                    NotificationSchema(
                        status=NotificationStatus.UNREAD,
                        company_id=company_id,
                        message=message,
                    ).model_dump()
                )
                manager = get_manager()
                await manager.broadcast_to_company(company_id, {"message": message})
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to create quiz. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            logger.info(f"Created quiz id: {quiz_id}")
            return quiz_id

    @staticmethod
    async def get_quiz_by_id(quiz_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.quizzes.get_quiz_by_id(
                    quiz_id=quiz_id, company_id=company_id
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if not quiz:
                raise NotFoundException(detail="Quiz not found")
            return QuizWithQuestionsDetailResponse(
                id=quiz.id,
                title=quiz.title,
                description=quiz.description or "",
                frequency=quiz.frequency,
                questions=[
                    QuestionWithAnswersDetailResponse(
                        id=q.id,
                        text=q.text,
                        answers=[
                            AnswerDetailResponse(
                                id=a.id, text=a.text, is_correct=a.is_correct
                            )
                            for a in q.answers
                        ],
                    )
                    for q in quiz.questions
                ],
            )

    @staticmethod
    async def get_all_quizzes(
        company_id: int,
        limit: int | None = None,
        offset: int | None = None,
        current_user_id: int = None,
    ):
        async with UnitOfWork() as uow:
            try:
                items, total_count = await uow.quizzes.get_all_quizzes(
                    current_user_id, company_id, limit, offset
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            logger.info(items)
            items = [
                QuizDetailResponse(
                    id=quiz.id,
                    title=quiz.title,
                    description=quiz.description,
                    frequency=quiz.frequency,
                    is_available=quiz.is_available,
                )
                for quiz in items
            ]

            return ListResponse[QuizDetailResponse](items=items, count=total_count)

    @staticmethod
    async def update_quiz(
        quiz_id: int,
        title: str,
        description: str,
        frequency: int,
        updated_questions: list[UpdatedQuestionSchema],
        updated_answers: list[UpdatedAnswerSchema],
    ):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.quizzes.get_one(id=quiz_id)
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if not quiz:
                raise NotFoundException(detail=f"Quiz with ID {quiz_id} not found")

            questions_to_updated = [
                {
                    key: value
                    for key, value in question.model_dump(exclude={"action"}).items()
                }
                for question in updated_questions
                if question.action == QuizActions.update.value
            ]
            answers_to_update = [
                {
                    key: value
                    for key, value in answer.model_dump(exclude={"action"}).items()
                }
                for answer in updated_answers
                if answer.action == QuizActions.update.value
            ]
            questions_to_delete = [
                question.model_dump()["id"]
                for question in updated_questions
                if question.action == QuizActions.delete.value
            ]
            answers_to_delete = [
                answer.model_dump()["id"]
                for answer in updated_answers
                if answer.action == QuizActions.delete.value
            ]
            questions_to_create = [
                {
                    key: value
                    for key, value in question.model_dump(exclude={"action"}).items()
                }
                for question in updated_questions
                if question.action == QuizActions.create.value
            ]
            answers_to_create = [
                {
                    key: value
                    for key, value in answer.model_dump(exclude={"action"}).items()
                }
                for answer in updated_answers
                if answer.action == QuizActions.create.value
            ]
            update_model = QuizUpdateSchema(
                title=title, description=description, frequency=frequency
            )
            try:
                await uow.quizzes.update(id=quiz_id, data=update_model.model_dump())

                if questions_to_create:
                    await uow.quizzes.save_questions_and_answers(
                        quiz_id=quiz_id,
                        questions=questions_to_create,
                        answers=answers_to_create,
                    )
                if questions_to_updated:
                    await uow.questions.update_many(questions_to_updated)
                if answers_to_update:
                    await uow.answers.update_many(answers_to_update)
                if questions_to_delete:
                    await uow.questions.delete_many(questions_to_delete)
                if answers_to_delete:
                    await uow.answers.delete_many(answers_to_delete)

            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to update quiz. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def delete_quiz(quiz_id):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.quizzes.get_one(id=quiz_id)
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if not quiz:
                raise NotFoundException(detail=f"Quiz with ID {quiz_id} not found")
            await uow.quizzes.delete(id=quiz_id)
            logger.info(f"Deleted quiz id: {quiz_id}")

    @staticmethod
    async def quiz_submit(data: QuizSubmitRequest, current_user_id: int):
        async with UnitOfWork() as uow:
            if current_user_id != data.user_id:
                raise ForbiddenException(
                    detail="You cannot submit a quiz for another user"
                )
            try:
                result = await uow.participants.get_one(
                    quiz_id=data.quiz_id, user_id=data.user_id
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if not result:
                try:
                    participant_id = await uow.participants.create(
                        QuizParticipantCreateSchema(
                            quiz_id=data.quiz_id, user_id=data.user_id
                        ).model_dump()
                    )
                except RepositoryIntegrityError as e:
                    logger.error(f"IntegrityError: {e}")
                    raise BadRequestException(
                        detail="Failed to create participant. Wrong data"
                    )
                except RepositoryDataError as e:
                    logger.error(f"Data error: {e}")
                    raise BadRequestException(
                        detail="Invalid format or length of fields"
                    )
                except RepositoryDatabaseError as e:
                    logger.error(f"SQLAlchemyError: {e}")
                    raise AppException(detail="Database exception occurred.")
                logger.info(f"Created quiz participant")
            else:
                participant = QuizParticipantDetailResponse.model_validate(result)
                participant_id = participant.id
                try:
                    await uow.participants.update(
                        id=participant_id,
                        data=QuizParticipantUpdateSchema(
                            completed_at=datetime.datetime.now()
                        ).model_dump(),
                    )
                except RepositoryIntegrityError as e:
                    logger.error(f"IntegrityError: {e}")
                    raise BadRequestException(
                        detail="Failed to update participant. Wrong data"
                    )
                except RepositoryDataError as e:
                    logger.error(f"Data error: {e}")
                    raise BadRequestException(
                        detail="Invalid format or length of fields"
                    )
                except RepositoryDatabaseError as e:
                    logger.error(f"SQLAlchemyError: {e}")
                    raise AppException(detail="Database exception occurred.")
            try:
                record_id = await uow.records.create(
                    RecordCreateSchema(
                        participant_id=participant_id, score=data.score
                    ).model_dump()
                )
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to create record. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            selected_answers = [
                SelectedAnswers(record_id=record_id, answer_id=answer.id)
                for question in data.questions
                for answer in question.answers
            ]
            try:
                answer_ids = await uow.answers.create_selected_answers(selected_answers)
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(
                    detail="Failed creating selected answers. Wrong data"
                )
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

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
            try:
                await quiz_redis_repo.save_answers(answers_data)
            except RedisRepositoryError as e:
                logger.error(f"Redis error: {e}")
                raise AppException(detail="Cache exception occurred.")
            return participant_id, record_id, answer_ids

    @staticmethod
    async def get_average_score_in_company(
        user_id: int,
        company_id: int,
        from_date: datetime.date,
        to_date: datetime.date,
    ):
        async with UnitOfWork() as uow:
            try:
                membership = await uow.memberships.get_one(
                    user_id=user_id, company_id=company_id
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if membership.role != RoleEnum.ADMIN and membership.role != RoleEnum.OWNER:
                raise ForbiddenException(detail="You dont have permissions for this")
            if from_date and to_date and from_date > to_date:
                raise BadRequestException(detail="Start date must be before end date")
            try:
                scores = await uow.records.get_average_score_in_company(
                    user_id, company_id, from_date, to_date
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            response = QuizAverageResponse(
                overall_average=float(scores[0]),
                scores=[
                    QuizScoreItem(
                        title="",
                        description="",
                        average_score=float(average_score),
                        completed_at=completed_at,
                    )
                    for _, average_score, completed_at in scores[1]
                ],
            )
            return response

    @staticmethod
    async def get_average_score_in_system(
        user_id: int,
        from_date: datetime.date = None,
        to_date: datetime.date = None,
    ):
        async with UnitOfWork() as uow:
            try:
                scores = await uow.records.get_average_score_in_system(
                    user_id, from_date, to_date
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            response = QuizAverageResponse(
                overall_average=float(scores[0]),
                scores=[
                    QuizScoreItem(
                        title=title,
                        description=description,
                        average_score=float(average_score),
                        completed_at=completed_at,
                    )
                    for title, description, completed_at, average_score in scores[1]
                ],
            )
            return response

    @staticmethod
    async def get_quiz_data_for_user(
        user_id: int = None,
        quiz_id: int = None,
        company_id: int = None,
        current_user_id: int = None,
    ):
        async with UnitOfWork() as uow:
            user_id = user_id if user_id is not None else current_user_id
            quiz_redis_repo = QuizRedisRepository(get_redis_client())
            try:
                answers = await quiz_redis_repo.get_answers_for_user(
                    user_id, quiz_id, company_id
                )
            except RedisRepositoryScanError as e:
                logger.error(f"Redis scan failed: {e}")
                raise AppException("Cache scan operation failed")
            except RedisRepositoryMultipleFetchError as e:
                logger.error(f"Redis mget failed: {e}")
                raise AppException("Cache get operation failed")
            answer_ids = [answer["answer_id"] for answer in answers]
            answers = list(answers)
            try:
                missing_answers = await uow.answers.get_missing_answers(
                    answer_ids, user_id, quiz_id, company_id
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            answers.extend(
                [
                    {
                        "answer_id": answer.id,
                    }
                    for answer in missing_answers
                ]
            )
            try:
                result = await uow.quizzes.get_full_quiz_data_for_user(
                    [answer["answer_id"] for answer in answers]
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            quiz_data = [
                {
                    "quiz_title": answer.quiz_title,
                    "quiz_description": answer.quiz_description,
                    "question_text": answer.question_text,
                    "answer_text": answer.answer_text,
                    "is_correct": answer.is_correct,
                }
                for answer in result
            ]
            return quiz_data


def get_quiz_service() -> QuizServices:
    return QuizServices()
