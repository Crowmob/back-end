import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, and_, update, select

from app.core.enums.enums import RoleEnum
from app.core.exceptions.exceptions import AppException, BadRequestException
from app.db.repositories.base_repository import BaseRepository
from app.models.membership_model import Memberships

logger = logging.getLogger(__name__)


class MembershipRepository(BaseRepository[Memberships]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Memberships)
