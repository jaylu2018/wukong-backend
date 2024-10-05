from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Generic, TypeVar, Type, List, Callable, Any, Optional, Dict
from pydantic import BaseModel
import time

from app.core.dependency import get_current_user, PermissionService
from app.models.base import LogType, LogDetailType
from app.schemas.base import Response, ResponseList
from app.core.log import insert_log

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
UserType = TypeVar("UserType")


class BaseCRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType, UserType]):
    def __init__(
            self,
            model: Type[ModelType],
            create_schema: Type[CreateSchemaType],
            update_schema: Type[UpdateSchemaType],
            service,
            log_detail_types: Dict[str, LogDetailType],
            get_current_user: Callable = get_current_user,
            permission_dependency: Callable = PermissionService.has_permission,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            pk: str = "id",
            log_type: LogType = LogType.AdminLog,
            unique_fields: Optional[List[str]] = None,
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.service = service
        self.get_current_user = get_current_user
        self.permission_dependency = permission_dependency
        self.pk = pk
        self.log_type = log_type
        self.log_detail_types = log_detail_types
        self.unique_fields = unique_fields or []
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._add_routes()

    def _add_routes(self):
        @self.router.get("", summary=f"获取{self.model.__name__}列表")
        async def list_items(
                request: Request,
                _: Any = Depends(self.permission_dependency),
                page: int = Query(1, description="页码"),
                page_size: int = Query(10, description="每页数量"),
        ):
            return await self._handle_request(
                self.log_detail_types["list"],
                self._list_items,
                request, page, page_size
            )

        @self.router.get(f"/{{{self.pk}:int}}", summary=f"获取单个{self.model.__name__}")
        async def get_item(
                pk: int,
                _: Any = Depends(self.permission_dependency),
        ):
            return await self._handle_request(
                self.log_detail_types["retrieve"],
                self._get_item,
                pk
            )

        @self.router.post("", summary=f"创建{self.model.__name__}")
        async def create_item(
                item_in: CreateSchemaType,
                _: Any = Depends(self.permission_dependency),
        ):
            return await self._handle_request(
                self.log_detail_types["create"],
                self._create_item,
                item_in
            )

        @self.router.patch(f"/{{{self.pk}:int}}", summary=f"更新{self.model.__name__}")
        async def update_item(
                pk: int,
                item_in: UpdateSchemaType,
                _: Any = Depends(self.permission_dependency),
        ):
            return await self._handle_request(
                self.log_detail_types["update"],
                self._update_item,
                pk, item_in
            )

        @self.router.delete(f"/{{{self.pk}:int}}", summary=f"删除{self.model.__name__}")
        async def delete_item(
                pk: int,
                _: Any = Depends(self.permission_dependency),
        ):
            return await self._handle_request(
                self.log_detail_types["delete"],
                self._delete_item,
                pk
            )

        @self.router.delete("/", summary=f"批量删除{self.model.__name__}")
        async def batch_delete_items(
                ids: str = Query(..., description=f"{self.model.__name__} ID 列表，以逗号分隔"),
                _: Any = Depends(self.permission_dependency),
        ):
            return await self._handle_request(
                self.log_detail_types["batch_delete"],
                self._batch_delete_items,
                ids
            )

    async def _handle_request(self, log_detail_type, handler, *args, **kwargs):
        start_time = time.time()
        try:
            return await handler(*args, **kwargs)
        finally:
            duration = time.time() - start_time
            await insert_log(log_type=self.log_type, log_detail_type=log_detail_type, detail=f"请求耗时 {duration:.2f} 秒")

    async def _list_items(self, request, page, page_size):
        query_params = dict(request.query_params)
        query_params.pop('page', None)
        query_params.pop('page_size', None)
        filters = {key: value for key, value in query_params.items()}
        total, items = await self.service.list(page=page, page_size=page_size, **filters)
        data = [await self.service.to_dict(item) for item in items]
        return ResponseList(data=data, total=total, current=page, size=page_size)

    async def _get_item(self, pk):
        item = await self.service.get(id=pk)
        if not item:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} 未找到")
        data = await self.service.to_dict(item)
        return Response(data=data)

    async def _create_item(self, item_in):
        if self.unique_fields:
            filters = {field: getattr(item_in, field) for field in self.unique_fields}
            existing_item = await self.service.get(**filters)
            if existing_item:
                conflict_fields = ", ".join(self.unique_fields)
                raise HTTPException(status_code=409, detail=f"{self.model.__name__}已存在，冲突字段：{conflict_fields}")
        item = await self.service.create(obj_in=item_in)
        return Response(data={"id": item.id})

    async def _update_item(self, pk, item_in):
        item = await self.service.update(id=pk, obj_in=item_in)
        if not item:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} 未找到")
        return Response(data={"id": pk})

    async def _delete_item(self, pk):
        success = await self.service.remove(id=pk)
        if not success:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} 未找到")
        return Response(data={"id": pk})

    async def _batch_delete_items(self, ids):
        id_list = [int(id.strip()) for id in ids.split(",") if id.strip().isdigit()]
        deleted_count = await self.service.batch_remove(id_list)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail=f"未找到指定的{self.model.__name__}")
        return Response(data={"deleted_ids": id_list})