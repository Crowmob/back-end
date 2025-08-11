import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.unit_of_work import UnitOfWork
from app.core.exceptions.company_exceptions import (
    CompanyWithIdNotFoundException,
    CompanyUpdateException,
    AppException,
)

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
            company_id = await uow.companies.create_company(
                owner=owner, name=name, description=description, private=private
            )
            logger.info(f"Company created: {name}")
            return company_id

    @staticmethod
    async def get_all_companies(limit: int | None = None, offset: int | None = None):
        async with UnitOfWork() as uow:
            try:
                companies = await uow.companies.get_all_companies(limit, offset)
                logger.info("Fetched companies")
                return companies
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise

    @staticmethod
    async def get_company_by_id_with_uow(company_id: int, uow: UnitOfWork):
        try:
            company = await uow.companies.get_company_by_id(company_id)
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
            values_to_update = {
                "name": name,
                "description": description,
                "private": private,
            }
            for key in list(values_to_update.keys()):
                if values_to_update[key] is None:
                    values_to_update.pop(key)
            logger.info(values_to_update)
            try:
                await uow.companies.update_company(company_id, values_to_update)

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
                await uow.companies.delete_company(company_id)
                logger.info(f"Company deleted: id={company_id}")

            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error: {e}")
                raise


company_services = CompanyServices()
