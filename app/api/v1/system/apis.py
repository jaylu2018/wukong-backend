from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from app.core.dependency import get_current_user, PermissionService
from app.models import Api, User
from app.models.base import LogDetailType, LogType, StatusType
from app.schemas.apis import ApiCreate, ApiUpdate, ApiOut
from app.schemas.base import Response, ResponseList
from app.services.apis import api_service
from app.api.base import BaseCRUDRouter
from app.core.log import insert_log
import time

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.ApiGetList,
    "retrieve": LogDetailType.ApiGetOne,
    "create": LogDetailType.ApiCreateOne,
    "update": LogDetailType.ApiUpdateOne,
    "delete": LogDetailType.ApiDeleteOne,
    "batch_delete": LogDetailType.ApiBatchDelete,
}


# 自定义的 ApiCRUDRouter
class ApiCRUDRouter(BaseCRUDRouter[Api, ApiCreate, ApiUpdate, User]):
    def _add_routes(self):

        # 重用父类的方法（获取单个、创建、更新、删除、批量删除）
        super()._add_routes()

        # 重写列表查询，以实现自定义的过滤和权限逻辑
        @self.router.get("", summary="获取 API 列表", response_model=ResponseList[List[ApiOut]])
        async def list_items(
                request: Request,
                current_user: User = Depends(self.get_current_user),
                page: int = Query(1, description="页码"),
                page_size: int = Query(10, description="每页数量"),
                path: Optional[str] = Query(None, description="API 路径"),
                summary: Optional[str] = Query(None, description="API 简介"),
                tags: Optional[str] = Query(None, description="API 标签，使用 '|' 分隔"),
                status: Optional[StatusType] = Query(None, description="API 状态"),
        ):
            start_time = time.time()
            try:
                # 构建过滤条件
                search_params = {
                    "path__icontains": path,
                    "summary__icontains": summary,
                    "tags__icontains": tags,
                    "status": status,
                }
                filters = {k: v for k, v in search_params.items() if v is not None}

                # 获取用户角色，判断是否为超级管理员
                user_roles = await current_user.roles.all()
                is_superuser = any(role.role_code == "R_SUPER" for role in user_roles)

                if is_superuser:
                    total, items = await self.service.list(page=page, page_size=page_size, order=["tags", "id"], **filters)
                else:
                    # 非超级管理员，只能查看自己角色下的 API
                    api_ids = set()
                    for role in user_roles:
                        role_apis = await role.apis.all()
                        api_ids.update(api.id for api in role_apis)
                    total = len(api_ids)
                    items = (await Api.filter(id__in=api_ids).filter(**filters).offset((page - 1) * page_size).limit(page_size).order_by("tags", "id"))

                data = [await self.service.to_dict(item) for item in items]
                return ResponseList(data=data, total=total, current=page, size=page_size)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["list"], detail=f"请求耗时 {duration:.2f} 秒")

        @self.router.get("/tree/", summary="获取API树形结构", response_model=Response[List[dict]])
        async def get_api_tree(current_user: User = Depends(self.get_current_user)):
            start_time = time.time()
            try:
                api_tree = await self.service.get_api_tree()
                return Response(data=api_tree)
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=LogDetailType.ApiGetTree,
                    detail=f"请求耗时 {duration:.2f} 秒"
                )


# 创建路由器实例
router = APIRouter()
api_router = ApiCRUDRouter(
    model=Api,
    create_schema=ApiCreate,
    update_schema=ApiUpdate,
    service=api_service,
    log_detail_types=log_detail_types,
    get_current_user=get_current_user,
    permission_dependency=PermissionService.has_permission,
    prefix="/apis",
    tags=["API管理"],
    log_type=LogType.AdminLog,
    pk="pk"
)

# 包含路由
router.include_router(api_router.router)
