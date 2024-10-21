from fastapi import APIRouter
from typing import List

from app.api.base import BaseCRUDRouter
from app.core.dependency import DependAuth
from app.models import Menu, User
from app.models.base import LogType, LogDetailType
from app.services.route import route_service
from app.schemas.base import Response
from app.schemas.route import RouteCreate, RouteUpdate
from app.core.log import insert_log

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.RouteGetList,
    "retrieve": LogDetailType.RouteGetOne,
    "create": LogDetailType.RouteCreateOne,
    "update": LogDetailType.RouteUpdateOne,
    "delete": LogDetailType.RouteDeleteOne,
    "batch_delete": LogDetailType.RouteBatchDelete,
    "exists": LogDetailType.RouteExists,
    "user_routes": LogDetailType.RouteGetUserRoutes,
    "constant_routes": LogDetailType.RouteGetConstantRoutes,
}


class RouteCRUDRouter(BaseCRUDRouter[Menu, RouteCreate, RouteUpdate, User]):
    def _add_routes(self):
        # 重用父类的方法
        super()._add_routes()

        # 自定义的路由是否存在接口
        @self.router.get("/{menu_name}/exists", summary="路由是否存在", dependencies=[DependAuth])
        async def route_exists(menu_name: str):
            is_exists = await Menu.exists(menu_name=menu_name)
            await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["exists"])
            return Response(data=is_exists)


# 创建路由器实例
router = APIRouter()
route_router = RouteCRUDRouter(
    model=Menu,
    create_schema=RouteCreate,
    update_schema=RouteUpdate,
    service=route_service,
    log_detail_types=log_detail_types,
    prefix="/routes",
    tags=["路由管理"],
    log_type=LogType.AdminLog,
    pk="pk",
)

router.include_router(route_router.router)
