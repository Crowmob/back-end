import json

import pytest
from sqlalchemy import select

from app.schemas.quiz import (
    AnswerSchema,
    QuestionWithAnswersSchema,
    QuizWithQuestionsSchema,
    QuizSubmitRequest,
    QuestionID,
    AnswerID,
    AnswerDetailResponse,
)
from app.models.quiz_model import Quiz, Question, Answer, QuizParticipant, Records


@pytest.mark.asyncio
async def test_create_quiz(db_session, quiz_services_fixture, test_company):
    quiz1 = QuizWithQuestionsSchema(
        id=1,
        title="Test Quiz",
        description="Test description",
        questions=[
            QuestionWithAnswersSchema(
                id=1,
                text="Test text",
                answers=[
                    AnswerDetailResponse(id=1, text="Test answer", is_correct=True),
                    AnswerDetailResponse(id=2, text="Test answer2", is_correct=False),
                ],
            ),
            QuestionWithAnswersSchema(
                id=2,
                text="Test text",
                answers=[
                    AnswerDetailResponse(id=3, text="Test answer", is_correct=True),
                    AnswerDetailResponse(id=4, text="Test answer2", is_correct=False),
                ],
            ),
        ],
    )
    quiz_id = await quiz_services_fixture.create_quiz(
        company_id=test_company["id"], quiz_id=None, quiz=quiz1
    )
    assert isinstance(quiz_id, int)


@pytest.mark.asyncio
async def test_get_all_quizzes(db_session, quiz_services_fixture, test_quiz):
    quizzes = await quiz_services_fixture.get_all_quizzes(
        company_id=test_quiz["company_id"], limit=5, offset=0
    )
    assert quizzes.count >= 1


@pytest.mark.asyncio
async def test_get_all_questions(db_session, quiz_services_fixture, test_questions):
    questions = await quiz_services_fixture.get_all_questions(
        quiz_id=test_questions["quiz_id"], limit=5, offset=0
    )
    assert questions.count == 2


@pytest.mark.asyncio
async def test_get_all_answers(db_session, quiz_services_fixture, test_answers):
    answers1 = await quiz_services_fixture.get_all_answers(
        question_id=test_answers["question_id1"]
    )
    assert len(answers1) == 2

    answers2 = await quiz_services_fixture.get_all_answers(
        question_id=test_answers["question_id2"]
    )
    assert len(answers2) == 2


@pytest.mark.asyncio
async def test_update_quiz(db_session, quiz_services_fixture, test_quiz):
    await quiz_services_fixture.update_quiz(
        quiz_id=test_quiz["id"], title="Test Title 2", description="Test Description 2"
    )
    quiz = await db_session.scalar(select(Quiz).where(Quiz.id == test_quiz["id"]))
    assert quiz.title == "Test Title 2"
    assert quiz.description == "Test Description 2"


@pytest.mark.asyncio
async def test_delete_quiz(
    db_session, quiz_services_fixture, test_quiz, test_questions, test_answers
):
    await quiz_services_fixture.delete_quiz(quiz_id=test_quiz["id"])

    quiz = await db_session.scalar(select(Quiz).where(Quiz.id == test_quiz["id"]))
    assert quiz is None
    for question_id in [test_questions["id1"], test_questions["id2"]]:
        question = await db_session.scalar(
            select(Question).where(Question.id == question_id)
        )
        assert question is None
    for answer_id in [
        test_answers["id1"],
        test_answers["id2"],
        test_answers["id3"],
        test_answers["id4"],
    ]:
        answer = await db_session.scalar(select(Answer).where(Answer.id == answer_id))
        assert answer is None


@pytest.mark.asyncio
async def test_delete_question(
    db_session, quiz_services_fixture, test_questions, test_answers
):
    for question_id in [test_questions["id1"], test_questions["id2"]]:
        await quiz_services_fixture.delete_question(question_id=question_id)
        question = await db_session.scalar(
            select(Question).where(Question.id == question_id)
        )
        assert question is None
    for answer_id in [
        test_answers["id1"],
        test_answers["id2"],
        test_answers["id3"],
        test_answers["id4"],
    ]:
        answer = await db_session.scalar(select(Answer).where(Answer.id == answer_id))
        assert answer is None


@pytest.mark.asyncio
async def test_delete_answer(db_session, quiz_services_fixture, test_answers):
    for answer_id in [
        test_answers["id1"],
        test_answers["id2"],
        test_answers["id3"],
        test_answers["id4"],
    ]:
        await quiz_services_fixture.delete_answer(answer_id=answer_id)
        answer = await db_session.scalar(select(Answer).where(Answer.id == answer_id))
        assert answer is None


@pytest.mark.asyncio
async def test_get_average_score_in_company(
    test_user,
    test_company,
    test_quiz,
    test_questions,
    test_answers,
    test_participant,
    test_record,
    quiz_services_fixture,
):
    score = await quiz_services_fixture.get_average_score_in_company(
        user_id=test_user["id"], company_id=test_company["id"]
    )
    assert score == 50


@pytest.mark.asyncio
async def test_get_average_score_in_system(
    test_user,
    test_quiz,
    test_questions,
    test_answers,
    test_participant,
    test_record,
    quiz_services_fixture,
):
    score = await quiz_services_fixture.get_average_score_in_system(
        user_id=test_user["id"]
    )
    assert score == 50


@pytest.mark.asyncio
async def test_quiz_submit(
    db_session,
    redis_client,
    test_user,
    test_company,
    test_quiz,
    test_questions,
    test_answers,
    quiz_services_fixture,
    monkeypatch,
):
    data = QuizSubmitRequest(
        score=1,
        quiz_id=test_quiz["id"],
        user_id=test_user["id"],
        company_id=test_company["id"],
        questions=[
            QuestionID(
                id=test_questions["id1"],
                answers=[
                    AnswerID(id=test_answers["id2"]),
                ],
            ),
            QuestionID(
                id=test_questions["id2"],
                answers=[
                    AnswerID(id=test_answers["id3"]),
                ],
            ),
        ],
    )
    participant_id, record_id = await quiz_services_fixture.quiz_submit(
        test_user["id"], data
    )

    participant = await db_session.execute(
        select(QuizParticipant).where(QuizParticipant.id == participant_id)
    )
    assert participant is not None
    result = await db_session.execute(select(Records).where(Records.id == record_id))
    record = result.scalars().first()
    assert record is not None
    assert record.score == 1

    cached_raw = await redis_client.get(
        f"{participant_id}:{record_id}:{data.questions[0].answers[0].id}"
    )
    cached_answer = json.loads(cached_raw.decode("utf-8"))
    assert cached_answer["company_id"] == data.company_id
