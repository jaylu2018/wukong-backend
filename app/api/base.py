from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from typing import Generic, TypeVar, Type, List, Callable, Any, Optional, Dict
from pydantic import BaseModel
import time

from app.core.dependency import PermissionService
from app.models.base import LogType, LogDetailType
from app.schemas.base import Response, ResponseList
from app.core.log import insert_log

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
UserType = TypeVar("UserType")
ListResponseModelType = TypeVar("ListResponseModelType")
GetResponseModelType = TypeVar("GetResponseModelType")
CreateResponseModelType = TypeVar("CreateResponseModelType")
UpdateResponseModelType = TypeVar("UpdateResponseModelType")
DeleteResponseModelType = TypeVar("DeleteResponseModelType")
BatchDeleteResponseModelType = TypeVar("BatchDeleteResponseModelType")


class BaseCRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType, UserType]):
    def __init__(
            self,
            model: Type[ModelType],
            create_schema: Type[CreateSchemaType],
            update_schema: Type[UpdateSchemaType],
            service,
            log_detail_types: Dict[str, LogDetailType],
            permission_dependency: Callable = PermissionService.has_permission,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            pk: str = "id",
            log_type: LogType = LogType.AdminLog,
            list_response_model: Optional[Type[ListResponseModelType]] = None,
            get_response_model: Optional[Type[GetResponseModelType]] = None,
            create_response_model: Optional[Type[CreateResponseModelType]] = None,
            update_response_model: Optional[Type[UpdateResponseModelType]] = None,
            delete_response_model: Optional[Type[DeleteResponseModelType]] = None,
            batch_delete_response_model: Optional[Type[BatchDeleteResponseModelType]] = None,
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.service = service
        self.permission_dependency = permission_dependency
        self.pk = pk
        self.log_type = log_type
        self.log_detail_types = log_detail_types
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.list_response_model = list_response_model
        self.get_response_model = get_response_model
        self.create_response_model = create_response_model
        self.update_response_model = update_response_model
        self.delete_response_model = delete_response_model
        self.batch_delete_response_model = batch_delete_response_model
        self._add_routes()

    def _add_routes(self):
        # 获取具体的 Pydantic 模型
        create_schema = self.create_schema
        update_schema = self.update_schema

        @self.router.get("", summary=f"获取{self.model.__name__}列表", response_model=self.list_response_model)
        async def list_items(
                request: Request,
                _: Any = Depends(self.permission_dependency),
                page: int = Query(1, description="页码"),
                size: int = Query(10, description="每页数量"),
        ):
            start_time = time.time()
            try:
                query_params = dict(request.query_params)
                # 移除分页参数
                query_params.pop('page', None)
                query_params.pop('size', None)
                # 处理过滤条件，转换为模型字段的过滤
                filters = {}
                for key, value in query_params.items():
                    filters[key] = value
                total, items = await self.service.list(page=page, size=size, **filters)
                data = [await self.service.to_dict(item) for item in items]
                return ResponseList(data={"list": data, "total": total, "current": page, "size": size})
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["list"], detail=f"请求耗时 {duration:.2f} 秒")

        @self.router.get(f"/{{{self.pk}:int}}", summary=f"获取单个{self.model.__name__}", response_model=self.get_response_model)
        async def get_item(
                pk: int,
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                item = await self.service.get(id=pk)
                data = await self.service.to_dict(item)
                return Response(data=data)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["retrieve"], detail=f"请求耗时 {duration:.2f} 秒")

        @self.router.post("", summary=f"创建{self.model.__name__}", response_model=self.create_response_model)
        async def create_item(
                item_in: create_schema = Body(...),
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                item = await self.service.create(item_in)
                return Response(data={"id": item.id})
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["create"], detail=f"请求耗时 {duration:.2f} 秒")

        @self.router.put(f"/{{{self.pk}:int}}", summary=f"更新{self.model.__name__}", response_model=self.update_response_model)
        async def update_item(
                pk: int,
                item_in: update_schema,
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                await self.service.update(id=pk, obj_in=item_in)
                return Response(data={"id": pk})
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["update"], detail=f"请求耗时 {duration:.2f} 秒")

        @self.router.delete(f"/{{{self.pk}:int}}", summary=f"删除{self.model.__name__}", response_model=self.delete_response_model)
        async def delete_item(
                pk: int,
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                await self.service.remove(id=pk)
                return Response(data={"id": pk})
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["delete"], detail=f"请求耗时 {duration:.2f} 秒")

        @self.router.delete("/", summary=f"批量删除{self.model.__name__}", response_model=self.batch_delete_response_model)
        async def batch_delete_items(
                ids: str = Query(..., description=f"{self.model.__name__} ID 列表，以逗号分隔"),
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                id_list = [int(id.strip()) for id in ids.split(",") if id.strip().isdigit()]
                await self.service.batch_remove(id_list)
                return Response(data={"deleted_ids": id_list})
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["batch_delete"], detail=f"请求耗时 {duration:.2f} 秒")
