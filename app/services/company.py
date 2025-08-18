import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.unit_of_work import UnitOfWork
from app.core.exceptions.company_exceptions import (
    CompanyWithIdNotFoundException,
    CompanyUpdateException,
    AppException,
)
from app.models.membership_model import RoleEnum
from app.schemas.company import CompanyUpdateRequestModel, CompanySchema
from app.schemas.membership import MembershipSchema

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
            company_id = await uow.companies.create(company.model_dump())
            logger.info(RoleEnum.OWNER.value)
            membership = MembershipSchema(
                user_id=owner, company_id=company_id, role=RoleEnum.OWNER.value
            )
            await uow.memberships.create(membership.model_dump())
            logger.info(f"Company created: {name}")
            return company_id

    @staticmethod
    async def get_all_companies(limit: int | None = None, offset: int | None = None):
        async with UnitOfWork() as uow:
            try:
                companies = await uow.companies.get_all_companies(limit, offset)
                logger.info("Fetched companies")
                logger.info(companies)
                return companies
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_company_by_id_with_uow(company_id: int, uow: UnitOfWork):
        try:
            company = await uow.companies.get_by_id(company_id)
            if not company:
                logger.warning(f"No company found with id={company_id}")
                raise CompanyWithIdNotFoundException(company_id)
            logger.info(f"Fetched company with id={company_id}")
            return company

        except SQLAlchemyError as e:
            logger.info(f"SQLAlchemy error: {e}")
            raise

    async def get_company_by_id(self, company_id: int):
        async with UnitOfWork() as uow:
            return await self.get_company_by_id_with_uow(company_id, uow)

    async def update_company(
        self,
        company_id: int,
        name: str | None = None,
        description: str | None = None,
        private: bool | None = True,
    ):
        async with UnitOfWork() as uow:
            await self.get_company_by_id_with_uow(company_id, uow)
            try:
                update_model = CompanyUpdateRequestModel(
                    name=name, description=description, private=private
                )
                await uow.companies.update(
                    company_id,
                    update_model.model_dump(),
                )

                logger.info(f"Company updated: id={company_id}")

            except IntegrityError as e:
                logger.error(f"Integrity error: {e}")
                raise CompanyUpdateException(company_id)

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise AppException(detail="Database exception occurred.")

    async def delete_company(self, company_id: int):
        async with UnitOfWork() as uow:
            await self.get_company_by_id_with_uow(company_id, uow)
            try:
                await uow.companies.delete(company_id)
                logger.info(f"Company deleted: id={company_id}")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


company_services = CompanyServices()
