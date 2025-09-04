import logging
from typing import Generic, TypeVar, Type

from sqlalchemy.exc import DataError, SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, insert, and_

from app.core.exceptions.exceptions import AppException, BadRequestException
from app.core.exceptions.repository_exceptions import (
    RepositoryIntegrityError,
    RepositoryDataError,
    RepositoryDatabaseError,
)

ModelType = TypeVar("ModelType")
logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, data: dict):
        try:
            new = self.model(**data)
            self.session.add(new)
            await self.session.flush()
            await self.session.refresh(new)
            return new.id
        except IntegrityError:
            raise RepositoryIntegrityError
        except DataError:
            raise RepositoryDataError
        except SQLAlchemyError:
            raise RepositoryDatabaseError

    async def create_many(self, data: list[dict]):
        try:
            if not data:
                return []
            stmt = insert(self.model).values(data).returning(self.model.id)
            result = await self.session.execute(stmt)
            return [row[0] for row in result.fetchall()]
        except IntegrityError:
            raise RepositoryIntegrityError
        except DataError:
            raise RepositoryDataError
        except SQLAlchemyError:
            raise RepositoryDatabaseError

    async def get_one(self, **filters):
        try:
            stmt = select(self.model).where(
                and_(
                    *(
                        getattr(self.model, field) == value
                        for field, value in filters.items()
                    )
                )
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError:
            raise RepositoryDatabaseError

    async def get_all(
        self,
        filters: dict[str, int | bool | list] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        extra_filters: list = None,
        joins: list[tuple] = None,
        outer_joins: list[tuple] = None,
        extra_columns: list = None,
    ):
        try:
            query = select(
                self.model,
                *(extra_columns or []),
                func.count().over().label("total_count"),
            ).distinct(self.model.id)

            if joins:
                for join_args in joins:
                    query = query.join(*join_args)

            if outer_joins:
                for join_args in outer_joins:
                    query = query.outerjoin(*join_args)

            if filters:
                for field, value in filters.items():
                    column = getattr(self.model, field)
                    if isinstance(value, list):
                        query = query.where(column.in_(value))
                    else:
                        query = query.where(column == value)

            if extra_filters:
                for f in extra_filters:
                    query = query.where(f)

            query = query.offset(offset or 0).limit(limit or 10)

            result = await self.session.execute(query)
            rows = result.all()

            if not rows:
                return [], 0

            if extra_columns:
                items = [tuple(row[:-1]) for row in rows]
            else:
                items = [row[0] for row in rows]

            total_count = rows[0][-1]
            return items, total_count
        except SQLAlchemyError:
            raise RepositoryDatabaseError

    async def update(self, data: dict, **filters):
        try:
            await self.session.execute(
                update(self.model)
                .where(
                    and_(
                        *(
                            getattr(self.model, field) == value
                            for field, value in filters.items()
                        )
                    )
                )
                .values(**data)
            )
        except IntegrityError:
            raise RepositoryIntegrityError
        except DataError:
            raise RepositoryDataError
        except SQLAlchemyError:
            raise RepositoryDatabaseError

    async def delete(self, **filters):
        try:
            await self.session.execute(
                delete(self.model).where(
                    and_(
                        *(
                            getattr(self.model, field) == value
                            for field, value in filters.items()
                        )
                    )
                )
            )
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemyError: {e}")
            raise AppException(detail="Database exception occurred.")
