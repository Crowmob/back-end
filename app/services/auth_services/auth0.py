import logging
import httpx
import os
import aiofiles

from fastapi import UploadFile

from app.core.exceptions.exceptions import NotFoundException
from app.schemas.response_models import ResponseModel
from app.services.user import get_user_service, UserServices
from app.utils.settings_model import settings

logger = logging.getLogger(__name__)


class Auth0UserServices:
    def __init__(self, user_service: UserServices):
        self.user_service = user_service

    async def auth_user(self, name: str, avatar: UploadFile | None, email: str):
        if avatar:
            ext = avatar.filename.split(".")[-1]
        else:
            ext = None
        user_id = await self.user_service.create_user(name, email, None, ext)
        if ext:
            filename = f"{user_id}.{ext}"
            filepath = os.path.join("static/avatars/", filename)
            async with aiofiles.open(filepath, "wb") as out_file:
                while content := await avatar.read(1024):
                    await out_file.write(content)
        return ResponseModel(
            status_code=200,
            message=f"Successfully authenticated user with email: {user_id}",
        )

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
        try:
            user = await self.user_service.get_user_by_email(email)
            if user:
                return {"message": "invalid_signup"}
        except NotFoundException:
            pass
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
            await self.user_service.create_user(username, email, password)
        logger.info(response)
        return response


def get_auth0_service() -> Auth0UserServices:
    return Auth0UserServices(get_user_service())
