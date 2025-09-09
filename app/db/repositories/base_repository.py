import logging
from typing import Generic, TypeVar, Type

from sqlalchemy.exc import DataError, SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, insert, and_, case, inspect

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
        except IntegrityError as e:
            raise RepositoryIntegrityError(f"Integrity error: {e}") from e
        except DataError as e:
            raise RepositoryDataError(f"Invalid data: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

    async def create_many(self, data: list[dict]):
        try:
            stmt = insert(self.model).values(data).returning(self.model.id)
            result = await self.session.execute(stmt)
            return [row[0] for row in result.fetchall()]
        except IntegrityError as e:
            raise RepositoryIntegrityError(f"Integrity error: {e}") from e
        except DataError as e:
            raise RepositoryDataError(f"Invalid data: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

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
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

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
            query = (
                select(self.model)
                .add_columns(
                    *(extra_columns or []), func.count().over().label("total_count")
                )
                .distinct(self.model.id)
            )

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

            items = []
            for row in rows:
                quiz_obj = row[0]
                if extra_columns:
                    for idx, col in enumerate(extra_columns, start=1):
                        setattr(quiz_obj, col.key, row[idx])
                items.append(quiz_obj)

            total_count = rows[0][-1]
            return items, total_count

        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

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
        except IntegrityError as e:
            raise RepositoryIntegrityError(f"Integrity error: {e}") from e
        except DataError as e:
            raise RepositoryDataError(f"Invalid data: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

    async def update_many(self, data: list[dict]):
        try:
            pk_col = inspect(self.model).primary_key[0]
            pk_name = pk_col.name

            ids = [row[pk_name] for row in data]

            stmt_values = {}
            for key in data[0].keys():
                if key == pk_name:
                    continue
                stmt_values[key] = case(
                    {row[pk_name]: row[key] for row in data}, value=pk_col
                )

            stmt = update(self.model).where(pk_col.in_(ids)).values(**stmt_values)

            await self.session.execute(stmt)
        except IntegrityError as e:
            raise RepositoryIntegrityError(f"Integrity error: {e}") from e
        except DataError as e:
            raise RepositoryDataError(f"Invalid data: {e}") from e
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e

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
            raise RepositoryDatabaseError(f"Database error: {e}") from e

    async def delete_many(self, ids: list[int]):
        try:
            await self.session.execute(delete(self.model).where(self.model.id.in_(ids)))
        except SQLAlchemyError as e:
            raise RepositoryDatabaseError(f"Database error: {e}") from e
