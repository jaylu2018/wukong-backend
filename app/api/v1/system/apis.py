from typing import List
from fastapi import APIRouter
from app.core.dependency import PermissionService
from app.models import Api, User
from app.models.base import LogDetailType, LogType
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

        @self.router.get("/tree/", summary="获取API树形结构", response_model=Response[List[dict]])
        async def get_api_tree():
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
    permission_dependency=PermissionService.has_permission,
    prefix="/apis",
    tags=["API管理"],
    log_type=LogType.AdminLog,
    pk="pk",
    list_response_model=ResponseList[List[ApiOut]],
)

# 包含路由
router.include_router(api_router.router)
