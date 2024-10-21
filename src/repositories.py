from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    model = None

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        pass

    @abstractmethod
    async def create_instance(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_instance(self, *args, **kwargs):
        pass

    @abstractmethod
    async def update_instance(self, *args, **kwargs):
        pass


class DBRepository(AbstractRepository):
    model = None

    @abstractmethod
    async def create_instance(self, *args, **kwargs):
        pass

    @abstractmethod
    async def get_list(self, *args, **kwargs):
        pass

    async def get_instance(self, id: int, session: AsyncSession):
        result = await session.scalars(select(self.model).where(self.model.id == id))
        return result.one_or_none()

    async def update_instance(self, id: int, data: dict, session: AsyncSession):
        data = data.model_dump()
        instance = await self.get_instance(id, session)

        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")

        for key, value in data.items():
            setattr(instance, key, value)

        session.add(instance)
        await session.commit()

        return instance

    async def delete_instance(self, id: int, session):
        instance = await self.get_instance(id, session)
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")

        await session.delete(instance)
        await session.commit()
