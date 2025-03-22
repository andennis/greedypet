from typing import TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import Select

ModelType = TypeVar("ModelType")

PRM_LIMIT = "limit"
PRM_ORDERBY = "order_by"


class BaseViewRepository(Generic[ModelType]):
    model: type[ModelType]  # Should be defined in subclasses

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, **kwargs) -> ModelType | None:
        result = await self._session.execute(select(self.model).filter_by(**kwargs))
        return result.scalar_one_or_none()

    async def execute_query(self, query: Select) -> list[ModelType]:
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_list(self, **kwargs) -> list[ModelType]:
        limit = kwargs.get("limit")
        order_by = kwargs.get("order_by")

        query = select(self.model)
        if limit:
            query = query.limit(limit)
        if order_by:
            query = query.order_by(order_by)

        for prm, val in kwargs.items():
            if prm not in [PRM_LIMIT, PRM_ORDERBY]:
                field = getattr(self.model, prm)
                query = query.where(field == val)

        return await self.execute_query(query)
