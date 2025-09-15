import pytest
import respx
from httpx import Response

from app.services.auth_services.auth0 import get_auth0_service
from app.utils.settings_model import settings


@pytest.mark.asyncio
async def test_auth_user():
    auth0_service = get_auth0_service()
    response = await auth0_service.auth_user(
        name="test", email="test@example.com", avatar=None
    )
    assert response.status_code == 200


@pytest.mark.asyncio
@respx.mock
async def test_login_user(test_user):
    respx.post(f"https://{settings.auth.AUTH0_DOMAIN}/oauth/token").mock(
        return_value=Response(200, json={"access_token": "fake-token"})
    )

    auth0_service = get_auth0_service()
    response = await auth0_service.login_user("test@example.com", "1234")
    assert response["access_token"] == "fake-token"
