import logging

from sqlalchemy.exc import SQLAlchemyError

from app.core.enums.enums import RoleEnum
from app.core.exceptions.exceptions import (
    AppException,
    NotFoundException,
    UnauthorizedException,
    BadRequestException,
)
from app.core.exceptions.repository_exceptions import (
    RepositoryDatabaseError,
    RepositoryIntegrityError,
    RepositoryDataError,
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
            try:
                result = await uow.memberships.update(
                    user_id=user_id,
                    company_id=company_id,
                    data={"role": RoleEnum.ADMIN},
                )
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to appoint admin. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if not result.rowcount:
                raise NotFoundException(
                    detail=f"User with id {user_id} is not member of company with id {company_id}"
                )
            logger.info(f"Appointed admin with id {user_id}")

    @staticmethod
    async def remove_admin(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                result = await uow.memberships.update(
                    user_id=user_id,
                    company_id=company_id,
                    data={"role": RoleEnum.MEMBER},
                )
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to remove admin. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            if not result.rowcount:
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
            try:
                items, total_count = await uow.users.get_all_admins(
                    company_id, limit, offset
                )
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
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
