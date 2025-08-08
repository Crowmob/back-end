import logging
from sqlalchemy.exc import SQLAlchemyError

from app.db.unit_of_work import UnitOfWork
from app.core.exceptions.membership_exceptions import (
    MembershipRequestWithIdNotFoundException,
)

logger = logging.getLogger(__name__)


class MembershipServices:
    @staticmethod
    async def send_membership_request(request_type: str, company_id: int, user_id: int):
        async with UnitOfWork() as uow:
            try:
                if request_type == "invitation":
                    membership_id = await uow.memberships.create_membership_request(
                        request_type, user_id, company_id
                    )
                elif request_type == "request":
                    membership_id = await uow.memberships.create_membership_request(
                        request_type, company_id, user_id
                    )
                logger.info("Created membership request")
                return membership_id
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def cancel_membership_request(request_id: int):
        async with UnitOfWork() as uow:
            try:
                await uow.memberships.delete_membership_request(request_id)
                logger.info(f"Deleted membership request with ID {request_id}")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def accept_membership_request(request_id: int):
        async with UnitOfWork() as uow:
            try:
                membership_request = await uow.memberships.get_membership_request_by_id(
                    request_id
                )
                if membership_request is None:
                    raise MembershipRequestWithIdNotFoundException(request_id)
                await uow.memberships.delete_membership_request(request_id)
                if membership_request.type == "request":
                    membership_id = await uow.memberships.create_membership(
                        membership_request.from_id, membership_request.to_id
                    )
                elif membership_request.type == "invitation":
                    membership_id = await uow.memberships.create_membership(
                        membership_request.to_id, membership_request.from_id
                    )
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
    async def get_all_memberships(
        company_id: int, limit: int | None = None, offset: int | None = None
    ):
        async with UnitOfWork() as uow:
            try:
                memberships = await uow.memberships.get_all_memberships(
                    company_id, limit, offset
                )
                return memberships
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
                    await uow.memberships.get_membership_requests_for_user(
                        request_type, user_id, limit, offset
                    )
                )
                return membership_requests
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_membership_requests_for_owner(
        request_type: str,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                membership_requests = (
                    await uow.memberships.get_membership_requests_for_owner(
                        user_id, request_type, limit, offset
                    )
                )
                return membership_requests
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


membership_services = MembershipServices()
