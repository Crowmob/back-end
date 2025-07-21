from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def truncate_users_table(session: AsyncSession):
    await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
    await session.commit()
