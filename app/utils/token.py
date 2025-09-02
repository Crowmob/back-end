import httpx
import logging

from datetime import datetime, timedelta

from fastapi import Header, Depends
from jose import JWTError, jwt
from jose import jwk as jose_jwk
from fastapi.security import HTTPBearer

from app.core.exceptions.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
)
from app.services.user import UserServices, get_user_service
from app.utils.settings_model import settings

AUTH0_DOMAIN = settings.auth.AUTH0_DOMAIN
API_AUDIENCE = settings.auth.API_AUDIENCE
ALGORITHM = settings.ALGORITHM
AUTH0_ALGORITHM = settings.auth.AUTH0_ALGORITHM

auth_scheme = HTTPBearer()

logger = logging.getLogger(__name__)


class TokenServices:
    @staticmethod
    async def decode_auth0_token(token: str):
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
                jwks = resp.json()
            except Exception:
                logger.exception("Failed to fetch JWKS")
                raise UnauthorizedException(detail="Failed to fetch JWKS")
        try:
            header = jwt.get_unverified_header(token)
        except Exception:
            logger.exception("Invalid header")
            raise UnauthorizedException(detail="Invalid header")

        rsa_key = None
        for key in jwks["keys"]:
            if key["kid"] == header["kid"]:
                rsa_key = jose_jwk.construct(key)
                break

        if not rsa_key:
            logger.exception("Public key not found")
            raise UnauthorizedException(detail="Public key not found.")

        try:
            payload = jwt.decode(
                token,
                key=rsa_key.to_pem().decode("utf-8"),
                algorithms=[AUTH0_ALGORITHM],
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

    async def get_data_from_token(
        self,
        authorization: str = Header(...),
        user_service: UserServices = Depends(get_user_service),
    ):
        token = authorization.removeprefix("Bearer ")
        if not token:
            raise UnauthorizedException(detail="Missing Bearer token")
        data = await self.decode_auth0_token(token)
        logger.info(data)
        email = data.get("email")
        if not email:
            raise UnauthorizedException(detail="Invalid token: no email claim")
        current_user = await user_service.get_user_by_email(data["email"])
        if not current_user:
            raise ConflictException("Authenticated user does not exist")
        return current_user

    @staticmethod
    def create_access_token(id: int):
        data = {"id": id}
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.EXP_TIME)
        to_encode.update({"exp": int(expire.timestamp())})
        logger.info("Created access token")
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str):
        try:
            data = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return data
        except JWTError:
            logger.error("Invalid token")
            raise UnauthorizedException(detail="Invalid token")


token_services = TokenServices()
