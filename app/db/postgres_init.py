from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import logging

from app.core.settings_model import settings
from app.db.models import Base

engine = create_async_engine(settings.db.URL, echo=True)
async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger = logging.getLogger(__name__)
        logger.info("Created tables")


async def disconnect_db():
    async with async_session_maker() as session:
        await session.close()



