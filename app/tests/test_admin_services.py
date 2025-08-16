import pytest

from sqlalchemy import select, and_

from app.models.membership_model import Memberships, RoleEnum


@pytest.mark.asyncio
async def test_appoint_admin(db_session, admin_services_fixture, test_membership):
    await admin_services_fixture.appoint_admin(
        test_membership["user_id"], test_membership["company_id"]
    )
    response = await db_session.execute(
        select(Memberships).where(
            and_(
                Memberships.user_id == test_membership["user_id"],
                Memberships.company_id == test_membership["company_id"],
            )
        )
    )
    membership = response.scalars().first()
    assert membership.role == RoleEnum.ADMIN


@pytest.mark.asyncio
async def test_remove_admin(db_session, admin_services_fixture, test_admin):
    await admin_services_fixture.remove_admin(
        test_admin["user_id"], test_admin["company_id"]
    )
    response = await db_session.execute(
        select(Memberships).where(
            and_(
                Memberships.user_id == test_admin["user_id"],
                Memberships.company_id == test_admin["company_id"],
            )
        )
    )
    membership = response.scalars().first()
    assert membership.role == RoleEnum.MEMBER


@pytest.mark.asyncio
async def test_get_all_admins(db_session, admin_services_fixture, test_admin):
    admins = await admin_services_fixture.get_all_admins(test_admin["company_id"])
    assert len(admins.items) >= 1
