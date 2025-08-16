import logging
from sqlalchemy.exc import SQLAlchemyError

from app.db.unit_of_work import UnitOfWork
from app.core.exceptions.membership_exceptions import (
    MembershipRequestWithIdNotFoundException,
)
from app.models.membership_model import RoleEnum
from app.schemas.membership import (
    MembershipRequestDetailResponse,
    MembershipRequestSchema,
    MembershipSchema,
)
from app.schemas.response_models import ListResponse
from app.schemas.user import UserDetailResponse
from app.schemas.company import CompanyDetailResponse

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
                if not membership_request:
                    membership_request = MembershipRequestSchema(
                        type=request_type, company_id=company_id, user_id=user_id
                    )
                    membership_id = await uow.membership_requests.create(
                        membership_request.model_dump()
                    )
                    logger.info("Created membership request")
                    return membership_id
                return membership_request.id
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def cancel_membership_request(request_id: int):
        async with UnitOfWork() as uow:
            try:
                await uow.membership_requests.delete(request_id)
                logger.info(f"Deleted membership request with ID {request_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def accept_membership_request(request_id: int):
        async with UnitOfWork() as uow:
            try:
                membership_request = await uow.membership_requests.get_by_id(request_id)
                if membership_request is None:
                    raise MembershipRequestWithIdNotFoundException(request_id)
                await uow.membership_requests.delete(request_id)
                membership = MembershipSchema(
                    role=RoleEnum.MEMBER.value,
                    user_id=membership_request.user_id,
                    company_id=membership_request.company_id,
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
                company_ids = [
                    request.company_id for request in membership_requests.items
                ]
                return await uow.companies.get_companies_by_ids(company_ids)
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
                membership_requests = (
                    await uow.membership_requests.get_membership_requests_to_company(
                        request_type, company_id, limit, offset
                    )
                )
                user_ids = [request.user_id for request in membership_requests.items]
                return await uow.users.get_users_by_ids(user_ids)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_companies_for_user(
        user_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                companies = await uow.companies.get_companies_for_user(
                    user_id, limit, offset
                )
                return companies
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_users_in_company(
        company_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                users = await uow.users.get_users_in_company(company_id, limit, offset)
                return users
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


membership_services = MembershipServices()
