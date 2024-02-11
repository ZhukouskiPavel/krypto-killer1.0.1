from typing import Generic, Type, TypeVar

from beanie import Document

ModelType = TypeVar("ModelType", bound=Document)


class BaseRepository(Generic[ModelType]):
    MODEL_CLASS: Type[ModelType]

    async def save(self, model: ModelType) -> None:
        await self.MODEL_CLASS.insert_one(model)

    async def bulk_save(self, models: list[ModelType]) -> None:
        await self.MODEL_CLASS.insert_many(models)
