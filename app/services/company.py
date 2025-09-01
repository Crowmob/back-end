import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError

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

logger = logging.getLogger(__name__)


class CompanyServices:
    @staticmethod
    async def create_company(
        owner: int,
        name: str,
        description: str | None = None,
        private: bool | None = True,
        email: str | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                company = CompanySchema(
                    owner=owner, name=name, description=description, private=private
                )
                company_id = await uow.companies.create(company.model_dump())
                logger.info(RoleEnum.OWNER.value)
                membership = MembershipSchema(
                    user_id=owner, company_id=company_id, role=RoleEnum.OWNER.value
                )
                await uow.memberships.create(membership.model_dump())
                logger.info(f"Company created: {name}")
                return company_id

            except DataError as e:
                logger.warning(f"Invalid data: {e}")
                raise BadRequestException(detail="Invalid format or length of fields")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException("Database exception occurred.")

    @staticmethod
    async def get_all_companies(
        limit: int | None = None,
        offset: int | None = None,
        email: str | None = None,
    ):
        async with UnitOfWork() as uow:
            try:
                if email:
                    user = await uow.users.get_user_by_email(email)
                else:
                    user = None
                if user:
                    (
                        items,
                        total_count,
                    ) = await uow.companies.get_all_companies_for_owner(
                        limit, offset, user.id
                    )
                else:
                    items, total_count = await uow.companies.get_all(
                        filters={"private": False}, limit=limit, offset=offset
                    )
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

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException("Database exception occurred.")

    @staticmethod
    async def get_company_by_id_with_uow(
        company_id: int, uow: UnitOfWork, email: str | None
    ):
        try:
            if email:
                current_user = await uow.users.get_user_by_email(email)
                if not current_user:
                    raise ConflictException(detail="Authenticated user does not exist")
            else:
                raise UnauthorizedException(detail="Unauthorized")
            result = await uow.companies.get_company_by_id(company_id, current_user.id)
            if not result:
                logger.warning(f"No company found with id={company_id}")
                raise NotFoundException(detail=f"No company found with id={company_id}")
            company = CompanyDetailResponse.model_validate(result)
            logger.info(f"Fetched company with id={company_id}")
            owner = await uow.users.get_by_id(company.owner)
            if email == owner.email:
                company.is_owner = True
            return company

        except SQLAlchemyError as e:
            logger.info(f"SQLAlchemy error: {e}")
            raise AppException("Database exception occurred.")

    async def get_company_by_id(self, company_id: int, email: str | None):
        async with UnitOfWork() as uow:
            return await self.get_company_by_id_with_uow(company_id, uow, email)

    async def update_company(
        self,
        company_id: int,
        name: str | None = None,
        description: str | None = None,
        private: bool | None = True,
        email: str | None = None,
    ):
        async with UnitOfWork() as uow:
            if not email:
                raise UnauthorizedException(detail="Unauthorized")
            await self.get_company_by_id_with_uow(company_id, uow, email)
            try:
                update_model = CompanyUpdateRequestModel(
                    name=name, description=description, private=private
                )
                await uow.companies.update(
                    company_id,
                    update_model.model_dump(),
                )

                logger.info(f"Company updated: id={company_id}")
                return ResponseModel(
                    status_code=200, message="Company updated successfully"
                )
            except IntegrityError as e:
                logger.error(f"Integrity error: {e}")
                raise BadRequestException(
                    detail=f"Failed to update company with id={company_id}. Wrong data"
                )

            except DataError as e:
                logger.warning(f"Data error: {e}")
                raise BadRequestException(detail=f"Invalid format or length of fields")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred.")

    async def delete_company(self, company_id: int, email: str | None):
        async with UnitOfWork() as uow:
            try:
                if not email:
                    raise UnauthorizedException(detail="Unauthorized")
                await self.get_company_by_id_with_uow(company_id, uow, email)
                await uow.companies.delete(company_id)
                logger.info(f"Company deleted: id={company_id}")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException("Database exception occurred.")


def get_company_service() -> CompanyServices:
    return CompanyServices()
