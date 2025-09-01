import datetime
import logging

from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

from app.core.enums.enums import RoleEnum
from app.core.exceptions.exceptions import (
    AppException,
    UnauthorizedException,
    NotFoundException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
)
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
    QuizWithQuestionsDetailResponse,
    QuestionWithAnswersDetailResponse,
    AnswerDetailResponse,
    QuizDetailResponse,
    QuizParticipantDetailResponse,
    QuizAverageResponse,
    QuizScoreItem,
)
from app.schemas.response_models import ListResponse

logger = logging.getLogger(__name__)


class QuizServices:
    @staticmethod
    async def create_quiz(
        company_id: int,
        quiz_id: int | str,
        quiz: QuizWithQuestionsSchema,
        email: str | None,
    ):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                quiz_id = None if quiz_id == "null" else int(quiz_id)
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

            except DataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def get_quiz_by_id(quiz_id: int, company_id: int, email: str | None):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                quiz = await uow.quizzes.get_quiz_by_id(quiz_id, company_id)
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
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def get_all_quizzes(
        company_id: int | None,
        email: str | None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                user = await uow.users.get_user_by_email(email)
                if not user:
                    raise ConflictException(detail="Authenticated user does not exist")
                items, total_count = await uow.quizzes.get_all_quizzes(
                    user.id, company_id, limit=limit, offset=offset
                )

                items = [
                    QuizDetailResponse(
                        id=quiz.id,
                        title=quiz.title,
                        description=quiz.description,
                        frequency=quiz.frequency,
                        is_available=quiz.is_available,
                        last_completed_at=quiz.last_completed_at,
                    )
                    for quiz in items
                ]

                return ListResponse[QuizDetailResponse](items=items, count=total_count)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def update_quiz(
        quiz_id: int, title: str | None = None, description: str | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.quizzes.get_by_id(quiz_id)
                if not quiz:
                    raise NotFoundException(detail=f"Quiz with ID {quiz_id} not found")
                update_model = QuizUpdateSchema(
                    title=title,
                    description=description,
                )
                await uow.quizzes.update(quiz_id, update_model.model_dump())
            except IntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to update quiz. Wrong data")
            except DataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def delete_quiz(quiz_id, email: str | None):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                quiz = await uow.quizzes.get_by_id(quiz_id)
                if not quiz:
                    raise NotFoundException(detail=f"Quiz with ID {quiz_id} not found")
                await uow.quizzes.delete(quiz_id)
                logger.info(f"Deleted quiz id: {quiz_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def quiz_submit(data: QuizSubmitRequest, email: str | None):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")

                current_user = await uow.users.get_user_by_email(email)
                if not current_user:
                    raise ConflictException(detail="Authenticated user does not exist")

                if current_user.id != data.user_id:
                    raise ForbiddenException(
                        detail="You cannot submit a quiz for another user"
                    )

                result = await uow.participants.get_quiz_participant(
                    data.quiz_id, data.user_id
                )
                if not result:
                    participant_id = await uow.participants.create(
                        QuizParticipantCreateSchema(
                            quiz_id=data.quiz_id, user_id=data.user_id
                        ).model_dump()
                    )
                    logger.info(f"Created quiz participant")
                else:
                    participant = QuizParticipantDetailResponse.model_validate(result)
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
            except IntegrityError as e:
                logger.warning(f"Invalid quiz submission data: {e}")
                raise BadRequestException(detail="Invalid quiz submission data")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            except RedisError as e:
                logger.error(f"RedisError: {e}")
                raise AppException(detail="Redis exception occurred.")

    @staticmethod
    async def get_average_score_in_company(
        user_id: int,
        company_id: int,
        from_date: datetime.date,
        to_date: datetime.date,
        email: str | None,
    ):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                current_user = await uow.users.get_user_by_email(email)
                if not current_user:
                    raise ConflictException(detail="Authenticated user does not exist")
                membership = await uow.memberships.get_membership(user_id, company_id)
                if (
                    membership.role != RoleEnum.ADMIN
                    and membership.role != RoleEnum.OWNER
                ):
                    raise ForbiddenException(
                        detail="You dont have permissions for this"
                    )
                if from_date and to_date and from_date > to_date:
                    raise BadRequestException(
                        detail="Start date must be before end date"
                    )
                scores = await uow.records.get_average_score_in_company(
                    user_id, company_id, from_date, to_date
                )
                response = QuizAverageResponse(
                    overall_average=float(scores[0]),
                    scores=[
                        QuizScoreItem(
                            quiz_id=quiz_id,
                            average_score=float(average_score),
                            completed_at=completed_at,
                        )
                        for quiz_id, _, average_score, completed_at in scores[1]
                    ],
                )
                logger.info(response)
                return response
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def get_average_score_in_system(
        user_id: int,
        from_date: datetime.date = None,
        to_date: datetime.date = None,
        email: str | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                if from_date and to_date and from_date > to_date:
                    raise AppException(detail="Start date must be before end date")
                scores = await uow.records.get_average_score_in_system(
                    user_id, from_date, to_date
                )
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
                logger.info(response)
                return response
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")

    @staticmethod
    async def get_quiz_data_for_user(
        email: str, user_id: int = None, quiz_id: int = None, company_id: int = None
    ):
        async with UnitOfWork() as uow:
            try:
                if email:
                    user = await uow.users.get_user_by_email(email)
                    if not user:
                        raise ConflictException(
                            detail="Authenticated user does not exist"
                        )
                else:
                    raise UnauthorizedException(detail="Unauthorized")
                user_id = user_id if user_id is not None else user.id
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

                result = await uow.quizzes.get_full_quiz_data_for_user(
                    [answer["answer_id"] for answer in answers]
                )
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
                logger.info(quiz_data)
                return quiz_data
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            except RedisError as e:
                logger.error(f"RedisError: {e}")
                raise AppException(detail="Redis exception occurred.")


def get_quiz_service() -> QuizServices:
    return QuizServices()
