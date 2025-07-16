from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete

from app.db.models import User
from app.schemas.user import UserSchema, ListResponse


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self) -> ListResponse[UserSchema]:
        result = await self.session.execute(select(User))
        users = result.scalars().all()
        return ListResponse[UserSchema](
            items=[UserSchema.model_validate(user) for user in users], count=len(users)
        )

    async def get_user_by_id(self, user_id: int) -> UserSchema | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return UserSchema.model_validate(user)
        return None

    async def create_user(self, user_data: UserSchema) -> int:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender,
        )
        self.session.add(new_user)
        await self.session.flush()
        return new_user.id

    async def update_user(self, user_id: int, values_to_update) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(**values_to_update)
        )

    async def delete_user(self, user_id: int) -> None:
        await self.session.execute(delete(User).where(User.id == user_id))
