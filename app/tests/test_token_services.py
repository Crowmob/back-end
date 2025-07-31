import pytest

from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import patch

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


@patch("app.utils.token.jwt.get_unverified_header")
@patch("app.utils.token.jwt.decode")
@patch(
    "app.utils.token.jwks",
    new={
        "keys": [
            {"kid": "test-kid", "kty": "RSA", "use": "sig", "n": "test-n", "e": "AQAB"}
        ]
    },
)
def test_decode_auth0_token(mock_decode, mock_get_header):
    mock_get_header.return_value = {"kid": "test-kid"}
    mock_decode.return_value = {
        "sub": "user123",
        "iss": f"https://{settings.AUTH0_DOMAIN}/",
        "aud": settings.API_AUDIENCE,
    }

    token = "fake-token"
    payload = token_services.decode_auth0_token(token)

    assert payload["sub"] == "user123"
