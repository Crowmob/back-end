from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete, func

from app.models.user_model import User, Identities
from app.schemas.user import UserDetailResponse, ListResponse


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> ListResponse[UserDetailResponse]:
        stmt = (
            select(User, func.count().over().label("total_count"))
            .offset(offset or 0)
            .limit(limit or 10)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        if not rows:
            return ListResponse[UserDetailResponse](items=[], count=0)

        total_count = rows[0][1]

        items = [
            UserDetailResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                password=user.password,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user, _ in rows
        ]

        return ListResponse[UserDetailResponse](items=items, count=total_count)

    async def get_user_by_id(self, user_id: int) -> UserDetailResponse | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            return UserDetailResponse.model_validate(user)
        return None

    async def get_user_by_email(self, email: int) -> UserDetailResponse | None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return UserDetailResponse.model_validate(user)
        return None

    async def create_user(
        self,
        username: str | None,
        email: str,
        password: str | None,
    ) -> int:
        new_user = User(
            username=username,
            email=email,
            password=password,
        )
        self.session.add(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        return new_user.id

    async def create_identity(
        self,
        user_id: int,
        provider: str,
        provider_id: str,
    ) -> None:
        new_identity = Identities(
            user_id=user_id,
            provider=provider,
            provider_id=provider_id,
        )
        self.session.add(new_identity)

    async def identity_exists(self, provider_id: str) -> bool:
        query = select(Identities).where(Identities.provider_id == provider_id)
        result = await self.session.execute(query)
        identity = result.scalar_one_or_none()
        return identity is not None

    async def update_user(self, user_id: int, values_to_update) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(**values_to_update)
        )

    async def delete_user(self, user_id: int) -> None:
        await self.session.execute(delete(User).where(User.id == user_id))
