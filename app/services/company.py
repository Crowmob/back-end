import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

from app.core.exceptions.repository_exceptions import (
    RepositoryDatabaseError,
    RepositoryIntegrityError,
    RepositoryDataError,
)
from app.db.unit_of_work import UnitOfWork
from app.core.exceptions.exceptions import (
    NotFoundException,
    BadRequestException,
    AppException,
    UnauthorizedException,
    ConflictException,
)
from app.models.membership_model import RoleEnum
from app.schemas.company import (
    CompanyUpdateRequestModel,
    CompanySchema,
    CompanyDetailResponse,
)
from app.schemas.membership import MembershipSchema
from app.schemas.response_models import ListResponse, ResponseModel
from app.schemas.user import UserDetailResponse

logger = logging.getLogger(__name__)


class CompanyServices:
    @staticmethod
    async def create_company(
        owner: int,
        name: str,
        description: str | None = None,
        private: bool | None = True,
    ):
        async with UnitOfWork() as uow:
            company = CompanySchema(
                owner=owner, name=name, description=description, private=private
            )
            try:
                company_id = await uow.companies.create(company.model_dump())
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to create company. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            membership = MembershipSchema(
                user_id=owner, company_id=company_id, role=RoleEnum.OWNER.value
            )
            try:
                await uow.memberships.create(membership.model_dump())
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to create company. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            logger.info(f"Company created: {name}")
            return company_id

    @staticmethod
    async def get_all_companies(
        limit: int | None = None,
        offset: int | None = None,
        current_user_id: int | None = None,
    ):
        async with UnitOfWork() as uow:
            if current_user_id is not None:
                try:
                    (
                        items,
                        total_count,
                    ) = await uow.companies.get_all_companies_for_owner(
                        limit, offset, current_user_id
                    )
                except RepositoryDatabaseError as e:
                    logger.error(f"SQLAlchemyError: {e}")
                    raise AppException(detail="Database exception occurred.")
            else:
                try:
                    items, total_count = await uow.companies.get_all(
                        filters={"private": False}, limit=limit, offset=offset
                    )
                except RepositoryDatabaseError as e:
                    logger.error(f"SQLAlchemyError: {e}")
                    raise AppException(detail="Database exception occurred.")
            companies = ListResponse[CompanyDetailResponse](
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
            logger.info("Fetched companies")
            logger.info(companies)
            return companies

    @staticmethod
    async def get_company_by_id_with_uow(
        company_id: int, uow: UnitOfWork, current_user_id: int, current_user_email: str
    ):
        result = await uow.companies.get_company_by_id(company_id, current_user_id)
        if not result:
            logger.warning(f"No company found with id={company_id}")
            raise NotFoundException(detail=f"No company found with id={company_id}")
        company = CompanyDetailResponse.model_validate(result)
        logger.info(f"Fetched company with id={company_id}")
        try:
            owner = await uow.users.get_one(id=company.owner)
        except RepositoryDatabaseError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")
        if current_user_email == owner.email:
            company.is_owner = True
        return company

    async def get_company_by_id(
        self, company_id: int, current_user_id: int, current_user_email: str
    ):
        async with UnitOfWork() as uow:
            return await self.get_company_by_id_with_uow(
                company_id, uow, current_user_id, current_user_email
            )

    async def update_company(
        self,
        company_id: int,
        name: str | None = None,
        description: str | None = None,
        private: bool | None = True,
        current_user_id: int = None,
        current_user_email: str = None,
    ):
        async with UnitOfWork() as uow:
            await self.get_company_by_id_with_uow(
                company_id, uow, current_user_id, current_user_email
            )
            update_model = CompanyUpdateRequestModel(
                name=name, description=description, private=private
            )
            try:
                await uow.companies.update(
                    id=company_id,
                    data=update_model.model_dump(),
                )
            except RepositoryIntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                raise BadRequestException(detail="Failed to update company. Wrong data")
            except RepositoryDataError as e:
                logger.error(f"Data error: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")
            except RepositoryDatabaseError as e:
                logger.error(f"SQLAlchemyError: {e}")
                raise AppException(detail="Database exception occurred.")
            logger.info(f"Company updated: id={company_id}")
            return ResponseModel(
                status_code=200, message="Company updated successfully"
            )

    async def delete_company(
        self,
        company_id: int,
        current_user_id: int = None,
        current_user_email: str = None,
    ):
        async with UnitOfWork() as uow:
            await self.get_company_by_id_with_uow(
                company_id, uow, current_user_id, current_user_email
            )
            await uow.companies.delete(company_id)
            logger.info(f"Company deleted: id={company_id}")


def get_company_service() -> CompanyServices:
    return CompanyServices()