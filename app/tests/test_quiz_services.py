import datetime
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
    QuizWithQuestionsDetailResponse,
)
from app.models.quiz_model import (
    Quiz,
    Question,
    Answer,
    QuizParticipant,
    Records,
    SelectedAnswers,
)


@pytest.mark.asyncio
async def test_create_quiz(db_session, quiz_services_fixture, test_company):
    quiz1 = QuizWithQuestionsSchema(
        title="Test Quiz",
        description="Test description",
        frequency=1,
        questions=[
            QuestionWithAnswersSchema(
                text="Test text",
                answers=[
                    AnswerDetailResponse(id=1, text="Test answer", is_correct=True),
                    AnswerDetailResponse(id=2, text="Test answer2", is_correct=False),
                ],
            ),
            QuestionWithAnswersSchema(
                text="Test text",
                answers=[
                    AnswerDetailResponse(id=3, text="Test answer", is_correct=True),
                    AnswerDetailResponse(id=4, text="Test answer2", is_correct=False),
                ],
            ),
        ],
    )
    quiz_id = await quiz_services_fixture.create_quiz(
        company_id=test_company["id"], quiz=quiz1
    )
    assert isinstance(quiz_id, int)


@pytest.mark.asyncio
async def test_get_quiz_by_id(db_session, quiz_services_fixture, test_quiz):
    quiz = await quiz_services_fixture.get_quiz_by_id(
        test_quiz["id"], test_quiz["company_id"]
    )
    assert isinstance(quiz, QuizWithQuestionsDetailResponse)


@pytest.mark.asyncio
async def test_get_all_quizzes(db_session, quiz_services_fixture, test_quiz):
    quizzes = await quiz_services_fixture.get_all_quizzes(
        company_id=test_quiz["company_id"],
        limit=5,
        offset=0,
        current_user_id=test_quiz["user_id"],
    )
    assert quizzes.count >= 1


@pytest.mark.asyncio
async def test_update_quiz(db_session, quiz_services_fixture, test_quiz):
    await quiz_services_fixture.update_quiz(
        quiz_id=test_quiz["id"],
        title="Test Title 2",
        description="Test Description 2",
        frequency=1,
        updated_answers=[],
        updated_questions=[],
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
async def test_get_average_score_in_company(
    test_quiz,
    test_questions,
    test_answers,
    test_participant,
    test_record,
    test_membership,
    quiz_services_fixture,
):
    from_date = datetime.date.today() - datetime.timedelta(days=1)
    to_date = datetime.date.today() + datetime.timedelta(days=1)

    scores = await quiz_services_fixture.get_average_score_in_company(
        user_id=test_membership["owner"],
        company_id=test_membership["company_id"],
        from_date=from_date,
        to_date=to_date,
    )
    assert scores.overall_average == 50
    assert len(scores.scores) == 1


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
    from_date = datetime.date.today() - datetime.timedelta(days=1)
    to_date = datetime.date.today() + datetime.timedelta(days=1)

    scores = await quiz_services_fixture.get_average_score_in_system(
        user_id=test_user["id"], from_date=from_date, to_date=to_date
    )
    assert scores.overall_average == 50
    assert len(scores.scores) == 1


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
    participant_id, record_id, answer_ids = await quiz_services_fixture.quiz_submit(
        data, test_user["id"]
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
        f"{test_user['id']}:{test_quiz['id']}:{test_company['id']}:{answer_ids[0]}"
    )
    cached_answer = json.loads(cached_raw.decode("utf-8"))
    assert cached_answer["company_id"] == data.company_id


@pytest.mark.asyncio
async def test_get_all_quizzes_data_for_user_in_company(
    quiz_services_fixture,
    redis_client,
    db_session,
    test_quiz,
    test_selected_answer,
    test_company,
    test_answers,
    test_participant,
    test_user,
    test_record,
):
    await redis_client.set(
        f"{test_user['id']}:{test_quiz['id']}:{test_company['id']}:{test_selected_answer['id']}",
        json.dumps(
            {
                "quiz_id": test_quiz["id"],
                "company_id": test_company["id"],
                "answer_id": test_selected_answer["id"],
                "participant_id": test_participant["id"],
                "user_id": test_user["id"],
                "record_id": test_selected_answer["record_id"],
            }
        ),
        ex=172800,
    )
    selected_answer = SelectedAnswers(
        answer_id=test_answers["id1"], record_id=test_record["id"]
    )
    db_session.add(selected_answer)
    await db_session.commit()

    data = await quiz_services_fixture.get_quiz_data_for_user(
        user_id=test_user["id"],
        company_id=test_company["id"],
        current_user_id=test_user["id"],
    )

    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_quiz_data_for_user_in_company(
    quiz_services_fixture,
    redis_client,
    db_session,
    test_quiz,
    test_selected_answer,
    test_company,
    test_answers,
    test_participant,
    test_user,
    test_record,
):
    await redis_client.set(
        f"{test_user['id']}:{test_quiz['id']}:{test_company['id']}:{test_selected_answer['id']}",
        json.dumps(
            {
                "quiz_id": test_quiz["id"],
                "company_id": test_company["id"],
                "answer_id": test_selected_answer["id"],
                "participant_id": test_participant["id"],
                "user_id": test_user["id"],
                "record_id": test_selected_answer["record_id"],
            }
        ),
        ex=172800,
    )
    selected_answer = SelectedAnswers(
        answer_id=test_answers["id1"], record_id=test_record["id"]
    )
    db_session.add(selected_answer)
    await db_session.commit()

    data = await quiz_services_fixture.get_quiz_data_for_user(
        user_id=test_user["id"],
        quiz_id=test_quiz["id"],
        company_id=test_company["id"],
        current_user_id=test_user["id"],
    )

    assert len(data) == 2


@pytest.mark.asyncio
async def test_all_quizzes_data_for_user(
    quiz_services_fixture,
    redis_client,
    db_session,
    test_quiz,
    test_selected_answer,
    test_company,
    test_answers,
    test_participant,
    test_user,
    test_record,
):
    await redis_client.set(
        f"{test_user['id']}:{test_quiz['id']}:{test_company['id']}:{test_selected_answer['id']}",
        json.dumps(
            {
                "quiz_id": test_quiz["id"],
                "company_id": test_company["id"],
                "answer_id": test_selected_answer["id"],
                "participant_id": test_participant["id"],
                "user_id": test_user["id"],
                "record_id": test_selected_answer["record_id"],
            }
        ),
        ex=172800,
    )
    selected_answer = SelectedAnswers(
        answer_id=test_answers["id1"], record_id=test_record["id"]
    )
    db_session.add(selected_answer)
    await db_session.commit()

    data = await quiz_services_fixture.get_quiz_data_for_user(
        user_id=test_user["id"], current_user_id=test_user["id"]
    )

    assert len(data) == 2
