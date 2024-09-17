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

    async def to_dict(self, obj: ModelType, exclude_fields: List[str] = None) -> dict:
        if exclude_fields is None:
            exclude_fields = []
        data = {}
        for field_name, field in obj._meta.fields_map.items():
            if field_name in exclude_fields:
                continue
            value = getattr(obj, field_name)
            if isinstance(field, fields.relational.ManyToManyFieldInstance):
                related_objects = await value.all()
                data[field_name] = [await self.to_dict(rel_obj) for rel_obj in related_objects]
            elif isinstance(field, fields.relational.ForeignKeyFieldInstance):
                related_object = await value
                data[field_name] = await self.to_dict(related_object) if related_object else None
            elif isinstance(field, fields.BackwardFKRelation):
                continue  # 忽略反向关系
            else:
                data[field_name] = value
        return data
