from abc import abstractmethod, ABC
from typing import Generic, TypeVar, Type, List, Any
from tortoise.models import Model
from pydantic import BaseModel

from app.core.log import logger

ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class CRUDBaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, id: int) -> ModelType:
        obj = await self.model.get_or_none(id=id)
        if not obj:
            raise ValueError(f"{self.model.__name__} ID 为 {id} 的对象未找到")
        return obj

    async def list(self, page: int = 1, size: int = 10, order: List[str] = None, **filters: Any) -> tuple[int, List[ModelType]]:
        if order is None:
            order = []
        query = self.model.filter(**filters)
        total = await query.count()
        result = await query.offset((page - 1) * size).limit(size).order_by(*order)
        return total, result

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)  # 或者使用 exclude_none=True
        obj = self.model(**obj_data)
        await obj.save()
        return obj

    async def update(self, id: int, obj_in: UpdateSchemaType) -> ModelType:
        db_obj = await self.get(id)
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        await db_obj.save()
        return db_obj

    async def remove(self, id: int) -> None:
        obj = await self.get(id)
        await obj.delete()

    async def batch_remove(self, ids: List[int]) -> int:
        deleted_count = await self.model.filter(id__in=ids).delete()
        if deleted_count == 0:
            raise ValueError(f"{self.model.__name__} 中未找到指定的对象")
        return deleted_count

    async def exists(self, **filters) -> bool:
        return await self.model.filter(**filters).exists()

    @abstractmethod
    async def to_dict(self, *args, **kwargs):
        """将模型实例转换为字典的抽象方法。"""
        pass
