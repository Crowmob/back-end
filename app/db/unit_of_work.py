from app.db.postgres_init import async_session_maker
from app.db.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self):
        self.session = None
        self.users: UserRepository = None

    async def __aenter__(self):
        if not self.session:
            self.session = async_session_maker()
            self.session = await self.session.__aenter__()
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
