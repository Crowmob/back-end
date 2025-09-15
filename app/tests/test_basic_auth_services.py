import pytest

from app.services.auth_services.basic import get_basic_auth_service


@pytest.mark.asyncio
async def test_register():
    basic_auth_service = get_basic_auth_service()
    response = await basic_auth_service.register(
        username="test", password="1234", email="test@example.com"
    )
    assert response.token


@pytest.mark.asyncio
async def test_login():
    basic_auth_service = get_basic_auth_service()
    response = await basic_auth_service.login(password="1234", email="test@example.com")
    assert response.token
