from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.repositories.user_repository_interface import IUserRepository
from app.schemas.user import UserSchema, UserUpdateRequestModel, UsersListResponse


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(self):
        result = await self.session.execute(
            text(
                "SELECT id, username, email, date_of_birth, gender, created_at FROM users"
            )
        )
        rows = result.fetchall()

        users = [
            UserSchema(
                username=row.username,
                email=row.email,
                password=row.password,
                date_of_birth=row.date_of_birth,
                gender=row.gender,
            )
            for row in rows
        ]

        return UsersListResponse(users=users)

    async def get_user_by_id(self, user_id: int):
        result = await self.session.execute(
            text(
                "SELECT username, email, password, date_of_birth, gender FROM users WHERE id = :id"
            ),
            {"id": user_id},
        )
        row = result.first()
        if row is None:
            return None
        return UserSchema(
            username=row.username,
            email=row.email,
            password=row.password,
            date_of_birth=row.date_of_birth,
            gender=row.gender,
        )

    async def create_user(self, user_data: UserSchema):
        await self.session.execute(
            text(
                "INSERT INTO users (username, email, password, date_of_birth, gender) "
                "VALUES (:username, :email, :password, :date_of_birth, :gender)"
            ),
            {
                "username": user_data.username,
                "email": user_data.email,
                "password": user_data.password,
                "date_of_birth": user_data.date_of_birth,
                "gender": user_data.gender,
            },
        )
        await self.session.flush()

        user_id = await self.session.execute(
            text("SELECT id FROM users WHERE email=:email"), {"email": user_data.email}
        )
        return user_id.first()[0]

    async def update_user(self, user_id: int, update_data: UserUpdateRequestModel):
        await self.session.execute(
            text(
                "UPDATE users SET "
                "username=COALESCE(:username, username), "
                "email=COALESCE(:email, email), "
                "password=COALESCE(:password, password), "
                "date_of_birth=COALESCE(:date_of_birth, date_of_birth) "
                "WHERE id=:id"
            ),
            {
                "id": user_id,
                "username": update_data.username,
                "email": update_data.email,
                "password": update_data.password,
                "date_of_birth": update_data.date_of_birth,
            },
        )

    async def delete_user(self, user_id: int):
        await self.session.execute(
            text("DELETE FROM users WHERE id=:id"), {"id": user_id}
        )
        await self.session.commit()
