from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, and_, Select

from app.models.user_model import User
from app.models.membership_model import Memberships
from app.schemas.user import (
    UserDetailResponse,
    MemberDetailResponse,
)
from app.schemas.response_models import ListResponse
from app.utils.settings_model import settings
from app.db.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def return_members(self, query: Select):
        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[UserDetailResponse](items=[], count=0)

        total_count = rows[0][2]
        items = [
            MemberDetailResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                about=user.about,
                role=role,
                avatar=f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                if user.avatar_ext
                else None,
            )
            for user, role, _ in rows
        ]
        return ListResponse[MemberDetailResponse](items=items, count=total_count)

    async def get_all_users(self, limit: int | None = None, offset: int | None = None):
        query = (
            select(User, func.count().over().label("total_count"))
            .where(User.has_profile)
            .offset(offset or 0)
            .limit(limit or 10)
        )

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return ListResponse[UserDetailResponse](items=[], count=0)

        total_count = rows[0].total_count

        items = [
            UserDetailResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                about=user.about,
                avatar=(
                    f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                    if user.avatar_ext
                    else None
                ),
            )
            for user, _ in rows
        ]

        return ListResponse[UserDetailResponse](items=items, count=total_count)

    async def get_user_by_email(self, email: int) -> UserDetailResponse | None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return UserDetailResponse.model_validate(user)
        return None

    async def delete_user(self, user_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**{"about": None, "has_profile": False})
        )

    async def get_users_in_company(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        query = (
            select(User, Memberships.role, func.count().over().label("total_count"))
            .join(Memberships, User.id == Memberships.user_id)
            .filter(Memberships.company_id == company_id)
            .limit(limit or 5)
            .offset(offset or 0)
        )

        return await self.return_members(query)

    async def get_users_by_ids(self, ids: list):
        if not ids:
            return ListResponse[UserDetailResponse](items=[], count=0)
        query = select(User, func.count().over().label("total_count")).where(
            User.id.in_(ids)
        )

        result = await self.session.execute(query)
        rows = result.all()

        total_count = rows[0][1]

        items = [
            UserDetailResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                about=user.about,
                avatar=(
                    f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                    if user.avatar_ext
                    else None
                ),
            )
            for user, _ in rows
        ]
        return ListResponse[UserDetailResponse](items=items, count=total_count)

    async def get_all_admins(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        query = (
            select(User, Memberships.role, func.count().over().label("total_count"))
            .join(
                Memberships,
                and_(User.id == Memberships.user_id, Memberships.role == "ADMIN"),
            )
            .filter(Memberships.company_id == company_id)
            .limit(limit or 5)
            .offset(offset or 0)
        )

        return await self.return_members(query)
