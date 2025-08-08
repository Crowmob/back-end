from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def truncate_users_table(session: AsyncSession):
    await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
    await session.commit()


async def truncate_companies_table(session: AsyncSession):
    await session.execute(text("TRUNCATE TABLE companies RESTART IDENTITY CASCADE;"))
    await session.commit()


async def truncate_memberships_table(session: AsyncSession):
    await session.execute(text("TRUNCATE TABLE memberships RESTART IDENTITY CASCADE;"))
    await session.commit()


async def truncate_membership_requests_table(session: AsyncSession):
    await session.execute(
        text("TRUNCATE TABLE membership_requests RESTART IDENTITY CASCADE;")
    )
    await session.commit()
