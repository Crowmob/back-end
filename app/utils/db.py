from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.models.user_model import User
from app.models.company_model import Company
from app.models.membership_model import Memberships, MembershipRequests


async def clear_tables(session: AsyncSession):
    await session.execute(delete(User))
    await session.execute(delete(Company))
    await session.execute(delete(Memberships))
    await session.execute(delete(MembershipRequests))
    await session.commit()
