import time

from fastapi import APIRouter, Depends
from typing import List

from app.api.base import BaseCRUDRouter
from app.core.log import insert_log
from app.models import Menu, User
from app.models.base import LogType, LogDetailType
from app.services.menu import menu_service
from app.schemas.base import Response, ResponseList
from app.schemas.menus import MenuCreate, MenuUpdate, MenuBase
from app.core.dependency import get_current_user

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


async def build_menu_tree(menus: List[Menu], parent_id: int = 0, simple: bool = False) -> List[dict]:
    """
    递归生成菜单树
    :param menus:
    :param parent_id:
    :param simple: 是否简化返回数据
    :return:
    """
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            children = await build_menu_tree(menus, menu.id, simple)
            if simple:
                menu_dict = {"id": menu.id, "label": menu.menu_name, "pId": menu.parent_id}
            else:
                menu_dict = await menu_service.to_dict(menu)
                menu_dict["buttons"] = [await button.to_dict() for button in await menu.buttons]
            if children:
                menu_dict["children"] = children
            tree.append(menu_dict)
    return tree


async def build_menu_button_tree(menus: List[Menu], parent_id: int = 0) -> List[dict]:
    """
    递归生成菜单按钮树
    :param menus:
    :param parent_id:
    :return:
    """
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            children = await build_menu_button_tree(menus, menu.id)
            menu_dict = {"id": f"parent${menu.id}", "label": menu.menu_name, "pId": menu.parent_id}
            if children:
                menu_dict["children"] = children
            else:
                menu_dict["children"] = [{"id": button.id, "label": button.button_code, "pId": menu.id} for button in await menu.buttons]
            tree.append(menu_dict)
    return tree


class MenuCRUDRouter(BaseCRUDRouter[Menu, MenuCreate, MenuUpdate, User]):
    def _add_routes(self):

        # 获取菜单树形结构
        @self.router.get("/tree/", summary="获取菜单树形结构", response_model=Response[List[dict]])
        async def get_menu_tree(role_id: int = None):
            start_time = time.time()
            try:
                if role_id:
                    menus = await self.service.get_menus_by_role(role_id)# 根据角色ID获取关联的菜单列表
                else:
                    menus = await self.service.get_non_constant_menus()# 获取所有非公共菜单
                menu_tree = await build_menu_tree(menus, simple=False)
                return Response(data=menu_tree)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_tree"], detail=f"请求耗时 {duration:.2f} 秒")

        # 查看一级菜单
        @self.router.get("/pages", summary="查看一级菜单", response_model=Response[List[str]])
        async def get_first_level_menus():
            start_time = time.time()
            try:
                menus = await self.service.get_first_level_menus()
                menu_names = [menu.route_name for menu in menus]
                return Response(data=menu_names)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_pages"], detail=f"请求耗时 {duration:.2f} 秒")

        # 获取菜单按钮树
        @self.router.get("/buttons/tree/", summary="查看菜单按钮树", response_model=Response[List[dict]])
        async def get_menu_button_tree():
            start_time = time.time()
            try:
                menus_with_buttons = await self.service.get_menus_with_buttons()
                menu_tree = await build_menu_button_tree(menus_with_buttons)
                return Response(data=menu_tree)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_buttons_tree"], detail=f"请求耗时 {duration:.2f} 秒")

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
    get_current_user=get_current_user,
    prefix="/menus",
    tags=["菜单管理"],
    log_type=LogType.AdminLog,
    pk='pk',
    list_response_model=ResponseList[List[MenuBase]]
)

router.include_router(menu_router.router)
