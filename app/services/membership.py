import logging
from sqlalchemy.exc import SQLAlchemyError

from app.db.unit_of_work import UnitOfWork
from app.core.exceptions.membership_exceptions import (
    MembershipRequestNotFoundException,
)
from app.core.enums.enums import RoleEnum
from app.schemas.company import CompanyDetailResponse
from app.schemas.membership import (
    MembershipRequestSchema,
    MembershipSchema,
    MembershipDetailResponse,
    MembershipRequestDetailResponse,
)
from app.schemas.response_models import ListResponse
from app.schemas.user import UserDetailResponse, MemberDetailResponse
from app.utils.settings_model import settings

logger = logging.getLogger(__name__)


class MembershipServices:
    @staticmethod
    async def send_membership_request(request_type: str, company_id: int, user_id: int):
        async with UnitOfWork() as uow:
            try:
                membership_request = (
                    await uow.membership_requests.get_membership_request(
                        request_type, company_id, user_id
                    )
                )
                logger.info(membership_request)
                if not membership_request:
                    new_request = MembershipRequestSchema(
                        type=request_type, company_id=company_id, user_id=user_id
                    )
                    membership_id = await uow.membership_requests.create(
                        new_request.model_dump()
                    )
                    logger.info("Created membership request")
                    return membership_id
                return membership_request.id
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_membership(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                result = await uow.memberships.get_membership(user_id, company_id)
                if not result:
                    return None
                return MembershipDetailResponse.model_validate(result)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def cancel_membership_request(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                await uow.membership_requests.delete_membership_request(
                    user_id, company_id
                )
                logger.info(f"Deleted membership request")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def accept_membership_request(
        request_type: str, user_id: int, company_id: int
    ):
        async with UnitOfWork() as uow:
            try:
                membership_request = (
                    await uow.membership_requests.get_membership_request(
                        request_type, company_id, user_id
                    )
                )
                if membership_request is None:
                    raise MembershipRequestNotFoundException()
                await uow.membership_requests.delete_membership_request(
                    user_id, company_id
                )
                membership = MembershipSchema(
                    role=RoleEnum.MEMBER.value,
                    user_id=user_id,
                    company_id=company_id,
                )
                membership_id = await uow.memberships.create(membership.model_dump())
                logger.info("Created membership successfully")
                return membership_id
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def delete_membership(user_id: int, company_id: int):
        async with UnitOfWork() as uow:
            try:
                await uow.memberships.delete_membership(
                    user_id=user_id, company_id=company_id
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_membership_requests_for_user(
        request_type: str,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                membership_requests = (
                    await uow.membership_requests.get_membership_requests_for_user(
                        request_type, user_id, limit, offset
                    )
                )
                company_ids = [request.company_id for request in membership_requests]
                items, total_count = await uow.companies.get_companies_by_ids(
                    company_ids
                )
                return ListResponse[CompanyDetailResponse](
                    items=[
                        CompanyDetailResponse(
                            id=company.id,
                            owner=company.owner,
                            name=company.name,
                            description=company.description,
                            private=company.private,
                        )
                        for company in items
                    ],
                    count=total_count,
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_membership_requests_to_company(
        request_type: str,
        company_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                result = (
                    await uow.membership_requests.get_membership_requests_to_company(
                        request_type, company_id, limit, offset
                    )
                )
                if not result:
                    membership_requests = ListResponse[MembershipRequestDetailResponse](
                        items=[], count=0
                    )

                total_count = result[0][1]
                items = [
                    MembershipRequestDetailResponse(
                        id=req.id,
                        type=req.type,
                        company_id=req.company_id,
                        user_id=req.user_id,
                    )
                    for req, _ in result
                ]

                membership_requests = ListResponse[MembershipRequestDetailResponse](
                    items=items, count=total_count
                )
                user_ids = [request.user_id for request in membership_requests.items]
                items, total_count = await uow.users.get_users_by_ids(user_ids)
                return ListResponse[UserDetailResponse](
                    items=[
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
                        for user in items
                    ],
                    count=total_count,
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_companies_for_user(
        user_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                result = await uow.companies.get_companies_for_user(
                    user_id, limit, offset
                )
                if not result:
                    return ListResponse[CompanyDetailResponse](items=[], count=0)

                total_count = result[0][2]

                items = [
                    CompanyDetailResponse(
                        id=company.id,
                        owner=company.owner,
                        name=company.name,
                        description=company.description,
                        private=company.private,
                        user_role=role,
                    )
                    for company, role, _ in result
                ]

                return ListResponse[CompanyDetailResponse](
                    items=items, count=total_count
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_users_in_company(
        company_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                result = await uow.users.get_users_in_company(company_id, limit, offset)
                if not result:
                    return ListResponse[MemberDetailResponse](items=[], count=0)

                total_count = result[0][2]
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
                    for user, role, _ in result
                ]
                return ListResponse[MemberDetailResponse](
                    items=items, count=total_count
                )
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


membership_services = MembershipServices()
