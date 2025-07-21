from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func
from typing import Optional

from app.models.user_model import User
from app.schemas.user import UserDetailResponse, ListResponse


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> ListResponse[UserDetailResponse]:
        stmt = select(User)

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        users = result.scalars().all()

        count_stmt = select(func.count()).select_from(User)
        total_count = await self.session.scalar(count_stmt)

        return ListResponse[UserDetailResponse](
            items=[UserDetailResponse.model_validate(user) for user in users],
            count=total_count,
        )

    async def get_user_by_id(self, user_id: int) -> UserDetailResponse | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return UserDetailResponse.model_validate(user)
        return None

    async def create_user(self, username: str, email: str, password: str) -> int:
        new_user = User(username=username, email=email, password=password)
        self.session.add(new_user)
        await self.session.flush()
        return new_user.id

    async def update_user(self, user_id: int, values_to_update) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(**values_to_update)
        )

    async def delete_user(self, user_id: int) -> None:
        await self.session.execute(delete(User).where(User.id == user_id))
