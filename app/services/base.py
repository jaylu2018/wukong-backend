from enum import Enum
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        return await self.model.get_or_none(id=id)

    async def list(
            self,
            page: int = 1,
            page_size: int = 10,
            order: List[str] = None,
            **filters: Any
    ) -> tuple[int, List[ModelType]]:
        if order is None:
            order = []
        query = self.model.filter(**filters)
        total = await query.count()
        result = await query.offset((page - 1) * page_size).limit(page_size).order_by(*order)
        return total, result

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)  # 或者使用 exclude_none=True
        obj = self.model(**obj_data)
        await obj.save()
        return obj

    async def update(self, id: int, obj_in: UpdateSchemaType) -> ModelType:
        db_obj = await self.get(id)
        if not db_obj:
            raise ValueError("Object not found")
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        await db_obj.save()
        return db_obj

    async def remove(self, id: int) -> None:
        obj = await self.get(id)
        if obj:
            await obj.delete()

    async def batch_remove(self, ids: List[int]) -> int:
        deleted_count = await self.model.filter(id__in=ids).delete()
        return deleted_count

    async def to_dict(self, obj: ModelType, exclude_fields: List[str] = None, visited: set = None) -> dict:
        if exclude_fields is None:
            exclude_fields = []
        if visited is None:
            visited = set()
        obj_id = (type(obj), obj.pk)
        if obj_id in visited:
            return {}  # 或者返回 {"id": obj.pk}
        visited.add(obj_id)
        data = {}
        for field_name, field in obj._meta.fields_map.items():
            if field_name in exclude_fields:
                continue
            value = getattr(obj, field_name)
            if isinstance(field, fields.relational.ForeignKeyFieldInstance):
                # 处理 ForeignKey，获取关联对象的字典表示
                related_obj = await value
                value = await self.to_dict(related_obj, exclude_fields, visited) if related_obj else None
            elif isinstance(field, fields.relational.ManyToManyFieldInstance):
                # 处理 ManyToManyField，获取关联对象列表的字典表示
                related_manager = getattr(obj, field_name)
                related_objs = await related_manager.all()
                value = [await self.to_dict(rel_obj, exclude_fields, visited) for rel_obj in related_objs]
            elif isinstance(field, fields.BackwardFKRelation):
                # 忽略反向关系
                continue
            elif isinstance(value, Enum):
                # 处理枚举类型
                value = value.value
            data[field_name] = value
        return data