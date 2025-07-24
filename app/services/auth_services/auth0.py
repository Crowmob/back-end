from app.services.user import user_services


class Auth0UserServices:
    @staticmethod
    async def auth_user(email: str, sub: str):
        sub = sub.split("|")
        auth_provider = sub[0]
        oauth_id = sub[1]
        await user_services.create_user(None, email, None, auth_provider, oauth_id)
        return email


auth0_user_services = Auth0UserServices()
