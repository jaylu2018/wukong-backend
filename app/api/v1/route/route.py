from fastapi import APIRouter, Depends
from typing import List

from app.api.base import BaseCRUDRouter
from app.core.context_vars import user_id_var
from app.core.dependency import DependAuth, get_current_user
from app.models import Menu, User, Role
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


async def build_route_tree(menus: List[Menu], parent_id: int = 0, simple: bool = False) -> List[dict]:
    """
    递归生成路由树
    :param menus:
    :param parent_id:
    :param simple: 是否简化返回数据
    :return:
    """
    tree = []
    for menu in menus:
        if menu.parent_id == parent_id:
            children = await build_route_tree(menus, menu.id, simple)
            if simple:
                menu_dict = {
                    "name": menu.route_name,
                    "path": menu.route_path,
                    "component": menu.component,
                    "meta": {
                        "title": menu.menu_name,
                        "i18nKey": menu.i18n_key,
                        "order": menu.order,
                        # "roles": role_codes,  # todo roles
                        "keepAlive": menu.keep_alive,
                        "icon": menu.icon,
                        "iconType": menu.icon_type,
                        "href": menu.href,
                        "activeMenu": menu.active_menu,
                        "multiTab": menu.multi_tab,
                        "fixedIndexInTab": menu.fixed_index_in_tab,
                    }
                }
                if menu.redirect:
                    menu_dict["redirect"] = menu.redirect
                if menu.component:
                    menu_dict["meta"]["layout"] = menu.component.split("$", maxsplit=1)[0]
                if menu.hide_in_menu and not menu.constant:
                    menu_dict["meta"]["hideInMenu"] = menu.hide_in_menu
            else:
                menu_dict = await menu.to_dict()
            if children:
                menu_dict["children"] = children
            tree.append(menu_dict)
    return tree


class RouteCRUDRouter(BaseCRUDRouter[Menu, RouteCreate, RouteUpdate, User]):
    def _add_routes(self):
        # 重用父类的方法
        super()._add_routes()

        # 自定义的路由是否存在接口
        @self.router.get("/{route_name}/exists", summary="路由是否存在", dependencies=[DependAuth])
        async def route_exists(route_name: str):
            is_exists = await Menu.exists(route_name=route_name)
            await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["exists"])
            return Response(data=is_exists)

        # 获取用户路由菜单
        @self.router.get("/user-routes", summary="查看用户路由菜单", dependencies=[DependAuth])
        async def get_user_routes():
            user_id = user_id_var.get()
            user_obj = await User.get(id=user_id)
            user_roles: List[Role] = await user_obj.roles.all()

            is_super = False
            role_home = "home"
            for user_role in user_roles:
                if user_role.role_code == "R_SUPER":
                    is_super = True
                if user_role.role_home:
                    role_home = user_role.role_home

            if is_super:
                role_routes = await Menu.filter(constant=False)
            else:
                role_routes = []
                for user_role in user_roles:
                    user_role_routes = await user_role.menus.all()
                    role_routes.extend(user_role_routes)

                # 获取所有父菜单
                menu_objs = role_routes.copy()
                while menu_objs:
                    menu = menu_objs.pop()
                    if menu.parent_id != 0:
                        parent_menu = await Menu.get(id=menu.parent_id)
                        if parent_menu not in role_routes:
                            role_routes.append(parent_menu)
                            menu_objs.append(parent_menu)

            role_routes = list(set(role_routes))
            menu_tree = await build_route_tree(role_routes, simple=True)
            data = {"home": role_home, "routes": menu_tree}
            await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["user_routes"])
            return Response(data=data)

        # 查看常量路由
        @self.router.get("/constant-routes", summary="查看常量路由(公共路由)")
        async def get_constant_routes():
            data = []
            menu_objs = await Menu.filter(constant=True, hide_in_menu=True)
            for menu_obj in menu_objs:
                route_data = {
                    "name": menu_obj.route_name,
                    "path": menu_obj.route_path,
                    "component": menu_obj.component,
                    "meta": {
                        "title": menu_obj.menu_name,
                        "i18nKey": menu_obj.i18n_key,
                        "constant": menu_obj.constant,
                        "hideInMenu": menu_obj.hide_in_menu
                    }
                }
                if menu_obj.props:
                    route_data["props"] = True
                data.append(route_data)
            await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["constant_routes"])
            return Response(data=data)


# 创建路由器实例
router = APIRouter()
route_router = RouteCRUDRouter(
    model=Menu,
    create_schema=RouteCreate,
    update_schema=RouteUpdate,
    service=route_service,
    log_detail_types=log_detail_types,
    get_current_user=get_current_user,
    prefix="/routes",
    tags=["路由管理"],
    log_type=LogType.AdminLog,
    pk="pk",
)

router.include_router(route_router.router)
