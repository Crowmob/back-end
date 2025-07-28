import httpx
import logging

from app.services.user import user_services
from app.utils.settings_model import settings
from app.utils.token import token_services

logger = logging.getLogger(__name__)


class Auth0UserServices:
    @staticmethod
    async def auth_user(name: str, email: str, sub: str):
        sub = sub.split("|")
        auth_provider = sub[0]
        oauth_id = sub[1]
        await user_services.create_user(name, email, None, auth_provider, oauth_id)
        return email

    @staticmethod
    async def login_user(email: str, password: str):
        url = f"https://{settings.auth.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "audience": settings.auth.API_AUDIENCE,
            "client_id": settings.auth.CLIENT_ID,
            "scope": "openid profile email",
            "connection": "Username-Password-Authentication",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
        if response.status_code != 200:
            logger.error("Auth0 login failed: %s", response.text)
        return response.json()

    async def register_user(self, username: str, email: str, password: str):
        url = f"https://{settings.auth.AUTH0_DOMAIN}/dbconnections/signup"
        payload = {
            "client_id": settings.auth.CLIENT_ID,
            "email": email,
            "password": password,
            "connection": "Username-Password-Authentication",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
        if response.status_code != 200:
            response = response.json()
            if response.get("code") == "invalid_signup":
                response["message"] = "invalid_signup"
            logger.error(f"Auth0 login failed: {response}")
            return response
        else:
            response = await self.login_user(email, password)
            sub = token_services.get_data_from_token(response["access_token"])[
                "sub"
            ].split("|")
            await user_services.create_user(username, email, password, sub[0], sub[1])
        logger.info(response)
        return response


auth0_user_services = Auth0UserServices()
