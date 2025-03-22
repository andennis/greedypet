from sqlalchemy import text

from .base_view import BaseViewRepository, ModelType


class BaseRepository(BaseViewRepository[ModelType]):
    async def commit(self):
        await self._session.commit()

    async def create(self, instance: ModelType) -> ModelType:
        self._session.add(instance)
        return instance

    async def delete(self, instance: ModelType):
        await self._session.delete(instance)

    # async def execute_procedure(self, ):
    #     await self._session.execute(text("CALL refresh_continuous_aggregate('trades_1min_ohlcv', '2025-03-21', '2025-03-23');"))
