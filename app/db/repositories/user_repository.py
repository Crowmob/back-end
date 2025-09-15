import logging
from datetime import datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_

from app.core.enums.enums import RoleEnum
from app.core.exceptions.repository_exceptions import RepositoryDatabaseError
from app.models.quiz_model import QuizParticipant
from app.models.user_model import User
from app.models.membership_model import Memberships
from app.db.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_all_users(self, limit: int | None = None, offset: int | None = None):
        items, total_count = await super().get_all(
            filters={"has_profile": True},
            limit=limit,
            offset=offset,
        )
        return items, total_count

    async def get_users_in_company(self, company_id: int, limit=None, offset=None):
        last_quiz_subq = (
            select(
                QuizParticipant.user_id,
                func.max(QuizParticipant.completed_at).label("last_quiz_time"),
            )
            .group_by(QuizParticipant.user_id)
            .subquery()
        )

        items, total_count = await super().get_all(
            limit=limit,
            offset=offset,
            joins=[(Memberships, User.id == Memberships.user_id)],
            outer_joins=[(last_quiz_subq, last_quiz_subq.c.user_id == User.id)],
            extra_filters=[Memberships.company_id == company_id],
            extra_columns=[Memberships.role, last_quiz_subq.c.last_quiz_time],
        )

        return items, total_count

    async def get_users_by_ids(self, ids: list[int]):
        items, total_count = await super().get_all(
            filters={"id": ids} if ids else {},
            limit=None,
            offset=None,
        )

        return items, total_count

    async def get_all_admins(self, company_id: int, limit=None, offset=None):
        items, total_count = await super().get_all(
            limit=limit,
            offset=offset,
            joins=[(Memberships, User.id == Memberships.user_id)],
            extra_filters=[
                Memberships.company_id == company_id,
                Memberships.role == RoleEnum.ADMIN,
            ],
            extra_columns=[Memberships.role],
        )

        return items, total_count

    async def get_users_with_quizzes_to_complete(self):
        try:
            one_day_ago = datetime.utcnow() - timedelta(days=1)
            start_of_day = one_day_ago.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_of_day = one_day_ago.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            stmt = (
                select(User)
                .outerjoin(QuizParticipant, QuizParticipant.user_id == User.id)
                .where(
                    or_(
                        QuizParticipant.completed_at.between(start_of_day, end_of_day),
                        QuizParticipant.id.is_(None),
                    )
                )
            )

            result = await self.session.execute(stmt)
            users = result.scalars().unique().all()
            return users
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e
