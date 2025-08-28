from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, and_, Select

from app.core.enums.enums import RoleEnum
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
            return None

        return rows

    async def get_all_users(self, limit: int | None = None, offset: int | None = None):
        items, total_count = await super().get_all(
            filters={"has_profile": True},
            limit=limit,
            offset=offset,
        )
        return items, total_count

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

    async def get_users_by_ids(self, ids: list[int]):
        if not ids:
            return [], 0
        items, total_count = await super().get_all(
            filters={"id": ids} if ids else {},
            limit=None,
            offset=None,
        )

        return items, total_count

    async def get_all_admins(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        query = (
            select(User, Memberships.role, func.count().over().label("total_count"))
            .join(
                Memberships,
                and_(
                    User.id == Memberships.user_id, Memberships.role == RoleEnum.ADMIN
                ),
            )
            .filter(Memberships.company_id == company_id)
            .limit(limit or 5)
            .offset(offset or 0)
        )

        return await self.return_members(query)
