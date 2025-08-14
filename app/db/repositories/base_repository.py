from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.schemas.base import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model

    async def create(self, data: CreateSchemaType):
        data = data.model_dump()
        new = self.model(**data)
        self.session.add(new)
        await self.session.flush()
        await self.session.refresh(new)
        return new.id

    async def get_by_id(self, obj_id: int):
        result = await self.session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def update(self, obj_id: int, data: UpdateSchemaType):
        data = data.model_dump(exclude_unset=True)
        await self.session.execute(
            update(self.model).where(self.model.id == obj_id).values(**data)
        )

    async def delete(self, obj_id: int):
        await self.session.execute(delete(self.model).where(self.model.id == obj_id))
