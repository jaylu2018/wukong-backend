import time

from fastapi import APIRouter, Depends, Request
from typing import List

from app.api.base import BaseCRUDRouter
from app.core.dependency import get_current_user
from app.core.log import insert_log
from app.models import Menu, User
from app.models.base import LogType, LogDetailType
from app.services.menu import menu_service
from app.schemas.base import Response, ResponseList
from app.schemas.menus import MenuCreate, MenuUpdate, MenuOut, MenuSearch
from app.services.user import user_service

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
        async def get_menu_tree(
                request: Request,
                current_user: User = Depends(get_current_user)
        ):
            start_time = time.time()
            try:
                role = await user_service.get_user_role(current_user.id)  # 获取当前用户的角色
                menus = await self.service.get_menus_by_role(role.id)
                query_params = dict(request.query_params)
                schema_fields = {field.alias: field_name for field_name, field in MenuSearch.model_fields.items() if field.alias}
                filters = {schema_fields.get(key, key): value for key, value in query_params.items()}
                filtered_menus = [
                    menu for menu in menus
                    if all(
                        value in getattr(menu, key, "") if key == "menu_name" else getattr(menu, key, None) == value
                        for key, value in filters.items()
                    )
                ]
                menu_tree = await self.service.build_menu_tree(filtered_menus)

                if not menu_tree and filtered_menus:
                    menu_list = [await self.service.to_dict(menu) for menu in filtered_menus]
                    return Response(data=menu_list)

                return Response(data=menu_tree)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_tree"], detail=f"请求耗时 {duration:.2f} 秒")

        super()._add_routes()  # 继承父类的方法（获取列表、获取单个、创建、更新、删除、批量删除）


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
