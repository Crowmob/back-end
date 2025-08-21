from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, insert

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, data: dict):
        new = self.model(**data)
        self.session.add(new)
        await self.session.flush()
        await self.session.refresh(new)
        return new.id

    async def create_many(self, data: list[dict]):
        if not data:
            return []
        stmt = insert(self.model).values(data).returning(self.model.id)
        result = await self.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def get_by_id(self, obj_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: dict[str, int | bool] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        query = select(self.model, func.count().over().label("total_count"))
        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field)
                if isinstance(value, list):
                    query = query.where(column.in_(value))
                else:
                    query = query.where(column == value)

        query = query.offset(offset or 0).limit(limit or 10)

        result = await self.session.execute(query)
        rows = result.all()

        if not rows:
            return [], 0

        total_count = rows[0].total_count
        items = [row[0] for row in rows]

        return items, total_count

    async def update(self, obj_id: int, data: dict):
        await self.session.execute(
            update(self.model).where(self.model.id == obj_id).values(**data)
        )

    async def delete(self, obj_id: int):
        await self.session.execute(delete(self.model).where(self.model.id == obj_id))
