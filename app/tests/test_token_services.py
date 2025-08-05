import pytest

from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import patch, AsyncMock

from app.utils.token import token_services
from app.utils.settings_model import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def test_create_and_decode_token():
    token = token_services.create_access_token(id=123)
    assert isinstance(token, str)

    data = token_services.decode_token(token)
    assert data["id"] == 123
    assert "exp" in data


@pytest.mark.asyncio
@patch("app.utils.token.TokenServices.decode_auth0_token")
async def test_get_data_from_token(mock_decode):
    mock_decode.return_value = {"id": 1}

    token = token_services.create_access_token(1)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    data = await token_services.get_data_from_token(credentials)
    assert data["id"] == 1


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get", new_callable=AsyncMock)
@patch("app.utils.token.jwt.get_unverified_header")
@patch("app.utils.token.jwt.decode")
async def test_decode_auth0_token(mock_jwt_decode, mock_get_header, mock_http_get):
    mock_response = AsyncMock()
    mock_response.json = lambda: {
        "keys": [
            {
                "kid": "test-kid",
                "kty": "RSA",
                "use": "sig",
                "alg": settings.auth.AUTH0_ALGORITHM,
                "n": "test-n",
                "e": "AQAB",
            }
        ]
    }
    mock_http_get.return_value = mock_response

    mock_get_header.return_value = {"kid": "test-kid"}

    mock_jwt_decode.return_value = {
        "sub": "user123",
        "iss": f"https://{settings.auth.AUTH0_DOMAIN}/",
        "aud": settings.auth.API_AUDIENCE,
    }

    token = "fake-token"
    payload = await token_services.decode_auth0_token(token)

    assert payload["sub"] == "user123"
