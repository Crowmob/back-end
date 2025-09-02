import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
)
from app.db.unit_of_work import UnitOfWork
from app.schemas.response_models import ListResponse, ResponseModel
from app.schemas.user import MemberDetailResponse
from app.utils.settings_model import settings

logger = logging.getLogger(__name__)


class AdminServices:
    @staticmethod
    async def appoint_admin(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            result = await uow.memberships.appoint_admin(user_id, company_id)
            if result.rowcount == 0:
                raise NotFoundException(
                    detail=f"User with id {user_id} is not member of company with id {company_id}"
                )
            logger.info(f"Appointed admin with id {user_id}")

    @staticmethod
    async def remove_admin(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            result = await uow.memberships.remove_admin(user_id, company_id)
            if result.rowcount == 0:
                raise NotFoundException(
                    detail=f"User with id {user_id} is not member of company with id {company_id}"
                )
            logger.info(f"Removed admin with id {user_id}")

    @staticmethod
    async def get_all_admins(
        company_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        async with UnitOfWork() as uow:
            items, total_count = await uow.users.get_all_admins(
                company_id, limit, offset
            )
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
                for user, role in items
            ]
            logger.info(items)
            return ListResponse[MemberDetailResponse](items=items, count=total_count)


def get_admin_service() -> AdminServices:
    return AdminServices()
