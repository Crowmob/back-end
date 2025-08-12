from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, and_

from app.models.user_model import User, Identities
from app.models.membership_model import Memberships
from app.schemas.user import UserDetailResponse, MemberDetailResponse
from app.schemas.response_models import ListResponse
from app.utils.settings_model import settings


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def return_members(self, stmt):
        result = await self.session.execute(stmt)
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

    async def get_all_users(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ):
        stmt = (
            select(User, func.count().over().label("total_count"))
            .where(User.has_profile)
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
                about=user.about,
                avatar=f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
                if user.avatar_ext
                else None,
            )
            for user, _ in rows
        ]
        return ListResponse[UserDetailResponse](items=items, count=total_count)

    async def get_user_by_id(self, user_id: int):
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None
        user_dict = user.__dict__.copy()
        if user_dict["avatar_ext"]:
            user_dict["avatar"] = (
                f"{settings.BASE_URL}/static/avatars/{user.id}.{user.avatar_ext}"
            )
        user_dict.pop("avatar_ext")
        return UserDetailResponse.model_validate(user_dict)

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
        avatar_ext: str | None = None,
    ) -> int:
        new_user = User(
            username=username, email=email, password=password, avatar_ext=avatar_ext
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
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**{"about": None, "has_profile": False})
        )

    async def get_users_in_company(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        stmt = (
            select(User, Memberships.role, func.count().over().label("total_count"))
            .join(Memberships, User.id == Memberships.user_id)
            .filter(Memberships.company_id == company_id)
            .limit(limit or 5)
            .offset(offset or 0)
        )

        return await self.return_members(stmt)

    async def get_all_admins(
        self, company_id: int, limit: int | None = None, offset: int | None = None
    ):
        stmt = (
            select(User, Memberships.role, func.count().over().label("total_count"))
            .join(
                Memberships,
                and_(User.id == Memberships.user_id, Memberships.role == "admin"),
            )
            .filter(Memberships.company_id == company_id)
            .limit(limit or 5)
            .offset(offset or 0)
        )

        return await self.return_members(stmt)
