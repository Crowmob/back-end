from app.core.exceptions.exceptions import UnauthorizedException
from app.schemas.response_models import AuthResponseModel, MeResponseModel
from app.services.user import get_user_service, UserServices
from app.utils.token import token_services
from app.utils.password import password_services


class BasicAuthServices:
    def __init__(self, user_service: UserServices):
        self.user_service = user_service

    async def register(self, username: str, email: str, password: str):
        user_id = await self.user_service.create_user(
            username, email, password, None, None
        )
        token = token_services.create_access_token(user_id)
        return AuthResponseModel(
            status_code=200, message="Registered successfully!", token=token
        )

    async def login(self, email: str, password: str):
        user = await self.user_service.get_user_by_email(email)
        if password_services.check_password(password, user.password):
            token = token_services.create_access_token(user.id)
            return AuthResponseModel(status_code=200, message="Logged in", token=token)
        raise UnauthorizedException(detail="Wrong password.")

    async def get_me(self, email: str | None):
        if not email:
            raise UnauthorizedException(detail="Invalid token.")
        user = await self.user_service.get_user_by_email(email)
        return MeResponseModel(status_code=200, me=user)


def get_basic_auth_service() -> BasicAuthServices:
    return BasicAuthServices(get_user_service())
