import time

from fastapi import APIRouter
from typing import List

from app.api.base import BaseCRUDRouter
from app.core.log import insert_log
from app.models import Menu, User
from app.models.base import LogType, LogDetailType
from app.services.menu import menu_service
from app.schemas.base import Response, ResponseList
from app.schemas.menus import MenuCreate, MenuUpdate, MenuOut

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.MenuGetList,
    "retrieve": LogDetailType.MenuGetOne,
    "create": LogDetailType.MenuCreateOne,
    "update": LogDetailType.MenuUpdateOne,
    "delete": LogDetailType.MenuDeleteOne,
    "batch_delete": LogDetailType.MenuBatchDeleteOne,
    "get_tree": LogDetailType.MenuGetTree,
    "get_pages": LogDetailType.MenuGetPages,
    "get_buttons_tree": LogDetailType.MenuGetButtonsTree,
}


class MenuCRUDRouter(BaseCRUDRouter[Menu, MenuCreate, MenuUpdate, User]):
    def _add_routes(self):

        # 获取菜单树形结构
        @self.router.get("/tree/", summary="获取菜单树形结构", response_model=Response[List[dict]])
        async def get_menu_tree(roleId: int = None):
            start_time = time.time()
            try:
                menus = await self.service.get_menus_by_role(roleId)
                menu_tree = await self.service.build_menu_tree(menus)
                return Response(data=menu_tree)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_tree"], detail=f"请求耗时 {duration:.2f} 秒")

        # 重用父类的方法（获取列表、获取单个、创建、更新、删除、批量删除）
        super()._add_routes()


# 创建路由器实例
router = APIRouter()
menu_router = MenuCRUDRouter(
    model=Menu,
    create_schema=MenuCreate,
    update_schema=MenuUpdate,
    service=menu_service,
    log_detail_types=log_detail_types,
    prefix="/menus",
    tags=["菜单管理"],
    log_type=LogType.AdminLog,
    pk='pk',
    list_response_model=ResponseList[List[MenuOut]]
)

router.include_router(menu_router.router)
