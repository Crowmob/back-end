from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.models.user_model import User
from app.models.company_model import Company
from app.models.membership_model import Memberships, MembershipRequests
from app.models.quiz_model import (
    Quiz,
    QuizParticipant,
    Question,
    Answer,
    Records,
    SelectedAnswers,
)


async def clear_tables(session: AsyncSession):
    await session.execute(delete(User))
    await session.execute(delete(Company))
    await session.execute(delete(Memberships))
    await session.execute(delete(MembershipRequests))
    await session.execute(delete(Quiz))
    await session.execute(delete(QuizParticipant))
    await session.execute(delete(Question))
    await session.execute(delete(Answer))
    await session.execute(delete(Records))
    await session.execute(delete(SelectedAnswers))
    await session.commit()
