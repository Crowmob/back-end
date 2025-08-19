import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.quiz_exceptions import QuizException, NotFoundByIdException
from app.db.unit_of_work import UnitOfWork
from app.schemas.quiz import (
    Quiz,
    Answer,
    Question,
    CreateQuestionSchema,
    CreateQuizSchema,
    CreateAnswerSchema,
    QuizUpdateModel,
    QuestionUpdateModel,
    AnswerUpdateModel,
)

logger = logging.getLogger(__name__)


class QuizServices:
    @staticmethod
    async def create_quiz(company_id: int, quiz: Quiz):
        async with UnitOfWork() as uow:
            if len(quiz.questions) < 2:
                raise QuizException(detail="Quiz should have at least 2 questions")
            try:
                quiz_id = await uow.quizzes.create(
                    CreateQuizSchema(
                        title=quiz.title,
                        description=quiz.description,
                        company_id=company_id,
                    ).model_dump()
                )
                for question in quiz.questions:
                    if 2 > len(question.answers) > 4:
                        raise QuizException(
                            detail="Questions should have at least 2 answers"
                        )
                    question_id = await uow.questions.create(
                        CreateQuestionSchema(
                            text=question.text, quiz_id=quiz_id
                        ).model_dump()
                    )
                    for answer in question.answers:
                        await uow.answers.create(
                            CreateAnswerSchema(
                                text=answer.text,
                                question_id=question_id,
                                is_correct=answer.is_correct,
                            ).model_dump()
                        )
                logger.info(f"Created quiz id: {quiz_id}")
                return quiz_id
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
                update_model = QuizUpdateModel(
                    title=title,
                    description=description,
                )
                await uow.quizzes.update(quiz_id, update_model.model_dump())
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def update_question(question_id: int, text: str | None = None):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.questions.get_by_id(question_id)
                if not quiz:
                    raise NotFoundByIdException(
                        detail=f"Question with id {question_id} not found"
                    )
                update_model = QuestionUpdateModel(text=text)
                await uow.questions.update(question_id, update_model.model_dump())
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise

    @staticmethod
    async def update_answer(
        answer_id: int, text: str | None = None, is_correct: bool | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                quiz = await uow.answers.get_by_id(answer_id)
                if not quiz:
                    raise NotFoundByIdException(
                        detail=f"Answer with id {answer_id} not found"
                    )
                update_model = AnswerUpdateModel(
                    text=text,
                    is_correct=is_correct,
                )
                await uow.answers.update(answer_id, update_model.model_dump())
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


quiz_services = QuizServices()
