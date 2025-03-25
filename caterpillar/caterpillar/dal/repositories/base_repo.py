from .base_view import BaseViewRepository, ModelType


class BaseRepository(BaseViewRepository[ModelType]):
    async def commit(self):
        await self._session.commit()

    def create(self, instance: ModelType) -> ModelType:
        self._session.add(instance)
        return instance

    async def delete(self, instance: ModelType):
        await self._session.delete(instance)
