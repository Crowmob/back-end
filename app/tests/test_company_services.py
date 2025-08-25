import pytest

from sqlalchemy import select, insert

from app.schemas.company import (
    CompanySchema,
    GetAllCompaniesRequest,
    CompanyUpdateRequestModel,
)
from app.models.company_model import Company


@pytest.mark.asyncio
async def test_create_company(db_session, company_services_fixture, test_user):
    company_data = CompanySchema(
        owner=test_user["id"], name="test", description="test", private=False
    )

    await company_services_fixture.create_company(
        test_user["id"],
        company_data.name,
        company_data.description,
        company_data.private,
    )

    db_company = await db_session.scalar(
        select(Company).where(Company.owner == test_user["id"])
    )
    assert db_company.name == company_data.name
    assert db_company.description == company_data.description


@pytest.mark.asyncio
async def test_get_all_companies(db_session, company_services_fixture, test_user):
    await db_session.execute(
        insert(Company).values(
            owner=test_user["id"], name="test1", description="test1", private=False
        )
    )
    await db_session.execute(
        insert(Company).values(
            owner=test_user["id"], name="test2", description="test2", private=False
        )
    )
    await db_session.commit()

    data = GetAllCompaniesRequest(limit=2)
    companies_list = await company_services_fixture.get_all_companies(
        data.limit, data.offset
    )
    assert len(companies_list.items) == 2


@pytest.mark.asyncio
async def test_get_company_by_id(company_services_fixture, test_membership):
    company = await company_services_fixture.get_company_by_id(
        test_membership["company_id"], test_membership["owner"]
    )

    assert company.name == "test"
    assert company.description == "test"


@pytest.mark.asyncio
async def test_update_company(db_session, company_services_fixture, test_membership):
    data = CompanyUpdateRequestModel(name="updated")
    await company_services_fixture.update_company(
        test_membership["company_id"],
        data.name,
        data.description,
        data.private,
        test_membership["owner"],
    )

    updated_company = await db_session.scalar(
        select(Company).where(Company.id == test_membership["company_id"])
    )
    assert updated_company.name == "updated"


@pytest.mark.asyncio
async def test_delete_company(db_session, company_services_fixture, test_membership):
    await company_services_fixture.delete_company(
        test_membership["company_id"], test_membership["owner"]
    )

    user = await db_session.scalar(
        select(Company).where(Company.id == test_membership["company_id"])
    )
    assert user is None
