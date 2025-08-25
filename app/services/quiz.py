import datetime
import json
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.quiz_exceptions import QuizException, NotFoundByIdException
from app.db.unit_of_work import UnitOfWork
from app.schemas.quiz import (
    QuizWithQuestionsSchema,
    QuestionCreateSchema,
    QuizCreateSchema,
    AnswerCreateSchema,
    QuizUpdateSchema,
    QuestionUpdateSchema,
    AnswerUpdateSchema,
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
        company_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                return await uow.quizzes.get_all_quizzes(company_id, limit, offset)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_all_questions(
        quiz_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                return await uow.questions.get_all_questions(quiz_id, limit, offset)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def get_all_answers(question_id: int):
        async with UnitOfWork() as uow:
            try:
                return await uow.answers.get_all_answers(question_id)
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
    async def delete_question(question_id):
        async with UnitOfWork() as uow:
            try:
                await uow.questions.delete(question_id)
                logger.info(f"Deleted question id: {question_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def delete_answer(answer_id):
        async with UnitOfWork() as uow:
            try:
                await uow.answers.delete(answer_id)
                logger.info(f"Deleted answer id: {answer_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def quiz_submit(user_id: int, data: QuizSubmitRequest):
        async with UnitOfWork() as uow:
            try:
                participant = await uow.participants.get_quiz_participant(
                    data.quiz_id, user_id
                )
                if not participant:
                    participant_id = await uow.participants.create(
                        QuizParticipantCreateSchema(
                            quiz_id=data.quiz_id, user_id=user_id
                        ).model_dump()
                    )
                    logger.info(f"Created quiz participant")
                else:
                    participant_id = participant.id
                    await uow.participants.update(
                        QuizParticipantUpdateSchema(
                            completed_at=datetime.datetime.now()
                        ).model_dump()
                    )
                record_id = await uow.records.create(
                    RecordCreateSchema(
                        participant_id=participant_id, score=data.score
                    ).model_dump()
                )
                for question in data.questions:
                    for answer in question.answers:
                        answer_data = {
                            "quiz_id": data.quiz_id,
                            "company_id": data.company_id,
                            "question_id": question.id,
                            "answer_id": answer.id,
                            "is_correct": answer.is_correct,
                        }
                        await uow.redis_base.set(
                            f"{participant_id}:{record_id}:{answer.id}",
                            answer_data,
                            172800,
                        )
                return participant_id, record_id
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


quiz_services = QuizServices()
