from app.services.user import user_services
from app.utils.token import token_services
from app.utils.password import password_services


class BasicAuthServices:
    @staticmethod
    async def register(username: str, email: str, password: str):
        user_id = await user_services.create_user(username, email, password, None, None)
        token = token_services.create_access_token(user_id)
        return token

    @staticmethod
    async def login(email: str, password: str):
        user = await user_services.get_user_by_email(email)
        if password_services.check_password(password, user.password):
            token = token_services.create_access_token(user.id)
            return token

    @staticmethod
    async def get_me(email: str):
        user = await user_services.get_user_by_email(email)
        return user


basic_auth_services = BasicAuthServices()
