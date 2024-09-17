from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from typing import Generic, TypeVar, Type, List, Callable, Any, Optional, Dict
from pydantic import BaseModel
import time

from app.core.dependency import get_current_user, PermissionService
from app.models.base import LogType, LogDetailType
from app.schemas.base import Success, SuccessExtra
from app.utils.public import insert_log

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
            log_type: LogType = LogType.AdminLog
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
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._add_routes()

    def _add_routes(self):
        @self.router.get("/", summary=f"获取{self.model.__name__}列表")
        async def list_items(
                request: Request,
                current_user: UserType = Depends(self.get_current_user),
                _: Any = Depends(self.permission_dependency),
                page: int = Query(1, description="页码"),
                page_size: int = Query(10, description="每页数量"),
        ):
            start_time = time.time()
            try:
                total, items = await self.service.list(page=page, page_size=page_size)
                data = [await self.service.to_dict(item) for item in items]
                return SuccessExtra(data=data, total=total, current=page, size=page_size)
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=self.log_detail_types["list"],
                    by_user_id=current_user.id,
                    # detail=f"请求耗时 {duration:.2f} 秒"
                )

        @self.router.get(f"/{{{self.pk}}}", summary=f"获取单个{self.model.__name__}")
        async def get_item(
                request: Request,
                pk: int,
                current_user: UserType = Depends(self.get_current_user),
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                item = await self.service.get(id=pk)
                if not item:
                    raise HTTPException(status_code=404, detail=f"{self.model.__name__} 未找到")
                data = await self.service.to_dict(item)
                return Success(data=data)
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=self.log_detail_types["retrieve"],
                    by_user_id=current_user.id,
                    # detail=f"请求耗时 {duration:.2f} 秒"
                )

        @self.router.post("/", summary=f"创建{self.model.__name__}")
        async def create_item(
                request: Request,
                item_in: CreateSchemaType,
                current_user: UserType = Depends(self.get_current_user),
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                item = await self.service.create(obj_in=item_in)
                return Success(data={"id": item.id})
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=self.log_detail_types["create"],
                    by_user_id=current_user.id,
                    # detail=f"请求耗时 {duration:.2f} 秒"
                )

        @self.router.patch(f"/{{{self.pk}}}", summary=f"更新{self.model.__name__}")
        async def update_item(
                request: Request,
                pk: int,
                item_in: UpdateSchemaType,
                current_user: UserType = Depends(self.get_current_user),
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                item = await self.service.update(id=pk, obj_in=item_in)
                if not item:
                    raise HTTPException(status_code=404, detail=f"{self.model.__name__} 未找到")
                return Success(data={"id": pk})
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=self.log_detail_types["update"],
                    by_user_id=current_user.id,
                    # detail=f"请求耗时 {duration:.2f} 秒"
                )

        @self.router.delete(f"/{{{self.pk}}}", summary=f"删除{self.model.__name__}")
        async def delete_item(
                request: Request,
                pk: int,
                current_user: UserType = Depends(self.get_current_user),
                _: Any = Depends(self.permission_dependency),
        ):
            start_time = time.time()
            try:
                success = await self.service.remove(id=pk)
                if not success:
                    raise HTTPException(status_code=404, detail=f"{self.model.__name__} 未找到")
                return Success(data={"id": pk})
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=self.log_detail_types["delete"],
                    by_user_id=current_user.id,
                    # detail=f"请求耗时 {duration:.2f} 秒"
                )
