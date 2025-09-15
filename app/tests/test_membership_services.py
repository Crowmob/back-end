import pytest
from sqlalchemy import select, insert

from app.models.membership_model import MembershipRequests, Memberships


@pytest.mark.asyncio
async def test_send_membership_request(
    db_session, membership_services_fixture, test_company, test_user
):
    membership_id = await membership_services_fixture.send_membership_request(
        "invite", test_company["id"], test_user["id"]
    )
    result = await db_session.execute(
        select(MembershipRequests).where(MembershipRequests.id == membership_id)
    )
    membership_request = result.scalar_one()
    assert membership_request.type == "invite"
    assert membership_request.company_id == test_company["id"]
    assert membership_request.user_id == test_user["id"]

    membership_id = await membership_services_fixture.send_membership_request(
        "request", test_company["id"], test_user["id"]
    )
    result = await db_session.execute(
        select(MembershipRequests).where(MembershipRequests.id == membership_id)
    )
    membership_request = result.scalar_one()
    assert membership_request.type == "request"
    assert membership_request.user_id == test_user["id"]
    assert membership_request.company_id == test_company["id"]


@pytest.mark.asyncio
async def test_cancel_membership_request(
    db_session, membership_services_fixture, test_membership_request
):
    await membership_services_fixture.cancel_membership_request(
        test_membership_request["user_id"], test_membership_request["company_id"]
    )
    result = await db_session.execute(
        select(MembershipRequests).where(
            MembershipRequests.id == test_membership_request["id"]
        )
    )
    membership_request = result.scalars().first()
    assert membership_request is None


@pytest.mark.asyncio
async def test_accept_membership_request(
    db_session, membership_services_fixture, test_membership_request
):
    membership_id = await membership_services_fixture.accept_membership_request(
        "request",
        test_membership_request["user_id"],
        test_membership_request["company_id"],
    )
    result = await db_session.execute(
        select(MembershipRequests).where(
            MembershipRequests.id == test_membership_request["id"]
        )
    )
    membership_request = result.scalars().first()
    assert membership_request is None
    result = await db_session.execute(
        select(Memberships).where(Memberships.id == membership_id)
    )
    membership = result.scalar_one()
    assert membership.id == membership_id


@pytest.mark.asyncio
async def test_delete_membership(
    db_session, membership_services_fixture, test_membership
):
    await membership_services_fixture.delete_membership(
        test_membership["user_id"], test_membership["company_id"]
    )
    result = await db_session.execute(
        select(Memberships).where(Memberships.id == test_membership["id"])
    )
    membership = result.scalars().first()
    assert membership is None


@pytest.mark.asyncio
async def test_get_companies_for_user(membership_services_fixture, test_membership):
    companies = await membership_services_fixture.get_companies_for_user(
        user_id=test_membership["user_id"], limit=5, offset=0
    )
    assert len(companies.items) >= 1


@pytest.mark.asyncio
async def test_get_users_in_company(membership_services_fixture, test_membership):
    users = await membership_services_fixture.get_users_in_company(
        company_id=test_membership["company_id"], limit=5, offset=0
    )
    assert len(users.items) >= 1


@pytest.mark.asyncio
async def test_get_membership_requests_for_user(
    membership_services_fixture, test_membership_request
):
    membership_requests = (
        await membership_services_fixture.get_membership_requests_for_user(
            "request", test_membership_request["user_id"], limit=5, offset=0
        )
    )
    assert len(membership_requests.items) >= 1
    membership_requests = (
        await membership_services_fixture.get_membership_requests_for_user(
            "invite", test_membership_request["user_id"], limit=5, offset=0
        )
    )
    assert len(membership_requests.items) == 0


@pytest.mark.asyncio
async def test_get_membership_requests_to_company(
    membership_services_fixture, test_membership_request
):
    membership_requests = (
        await membership_services_fixture.get_membership_requests_to_company(
            "request", test_membership_request["company_id"], limit=5, offset=0
        )
    )
    assert len(membership_requests.items) >= 1
    membership_requests = (
        await membership_services_fixture.get_membership_requests_to_company(
            "invite", test_membership_request["company_id"], limit=5, offset=0
        )
    )
    assert len(membership_requests.items) == 0
