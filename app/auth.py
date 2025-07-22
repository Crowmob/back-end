import requests
import logging

from jose import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.exceptions.auth_exceptions import UnauthorizedException
from app.core.settings_model import settings

AUTH0_DOMAIN = settings.AUTH0_DOMAIN
API_AUDIENCE = settings.API_AUDIENCE
ALGORITHM = settings.ALGORITHM

auth_scheme = HTTPBearer()

jwks = requests.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json").json()

logger = logging.getLogger(__name__)


def verify_jwt(token: str):
    try:
        header = jwt.get_unverified_header(token)
    except Exception:
        logger.exception("Invalid header")
        raise UnauthorizedException(detail="Invalid header")

    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break

    if not rsa_key:
        logger.exception("Public key not found")
        raise UnauthorizedException(detail="Public key not found.")

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[ALGORITHM],
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise UnauthorizedException(detail="Token expired.")
    except jwt.JWTClaimsError:
        logger.error("Incorrect claims")
        raise UnauthorizedException(detail="Incorrect claims.")


def get_data_from_token(
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
):
    return verify_jwt(credentials.credentials)
