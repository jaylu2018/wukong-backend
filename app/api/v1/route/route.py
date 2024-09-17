from fastapi import APIRouter, Depends
from typing import List

from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth, get_current_user
from app.models import Menu, User, Role
from app.models.base import LogType, LogDetailType
from app.services.route import route_service
from app.schemas.base import Success
from app.schemas.route import RouteCreate, RouteUpdate
from app.utils.public import insert_log

router = APIRouter()


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


@router.get("/constant-routes", summary="查看常量路由(公共路由)")
async def get_constant_routes():
    """
    查看常量路由
    :return:
    """
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

    return Success(data=data)


@router.get("/user-routes", summary="查看用户路由菜单", dependencies=[DependAuth])
async def get_user_routes():
    """
    查看用户路由菜单, 超级管理员返回所有菜单
    :return:
    """
    user_id = CTX_USER_ID.get()
    user_obj = await User.get(id=user_id)
    user_roles: list[Role] = await user_obj.roles

    is_super = False
    role_home = "home"
    for user_role in user_roles:
        if user_role.role_code == "R_SUPER":
            is_super = True
        if user_role.role_home:
            role_home = user_role.role_home

    if is_super:
        role_routes: list[Menu] = await Menu.filter(constant=False)  # todo 处理隐藏菜单是否需要返回
    else:
        role_routes: list[Menu] = []
        for user_role in user_roles:
            user_role_routes: list[Menu] = await user_role.menus  # type: ignore
            for user_role_route in user_role_routes:
                if not user_role_route.constant or user_role_route.hide_in_menu:
                    role_routes.append(user_role_route)

        menu_objs = role_routes.copy()
        while len(menu_objs) > 0:
            menu = menu_objs.pop()
            if menu.parent_id != 0:
                menu = await Menu.get(id=menu.parent_id)
                menu_objs.append(menu)
            else:
                role_routes.append(menu)

    role_routes = list(set(role_routes))  # 去重
    # 递归生成菜单
    menu_tree = await build_route_tree(role_routes, simple=True)
    data = {"home": role_home, "routes": menu_tree}
    return Success(data=data)


@router.get("/{route_name}/exists", summary="路由是否存在", dependencies=[DependAuth])
async def route_exists(route_name: str):
    is_exists = await Menu.exists(route_name=route_name)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RouteExists, by_user_id=CTX_USER_ID.get())
    return Success(data=is_exists)


@router.get("/routes", summary="获取路由列表")
async def get_routes(current_user: User = Depends(get_current_user)):
    routes = await route_service.get_routes()
    route_tree = await build_route_tree(routes, simple=True)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RouteGetList, by_user_id=current_user.id)
    return Success(data=route_tree)


@router.post("/routes", summary="创建路由")
async def create_route(route_in: RouteCreate, current_user: User = Depends(get_current_user)):
    new_route = await route_service.create(route_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RouteCreateOne, by_user_id=current_user.id)
    return Success(msg="Created Successfully", data={"created_id": new_route.id})


@router.patch("/routes/{route_id}", summary="更新路由")
async def update_route(route_id: int, route_in: RouteUpdate, current_user: User = Depends(get_current_user)):
    updated_route = await route_service.update(route_id, route_in)
    if updated_route:
        await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RouteUpdateOne, by_user_id=current_user.id)
        return Success(msg="Updated Successfully", data={"updated_id": route_id})
    return Success(msg="Route not found", data=None)


@router.delete("/routes/{route_id}", summary="删除路由")
async def delete_route(route_id: int, current_user: User = Depends(get_current_user)):
    deleted = await route_service.delete(route_id)
    if deleted:
        await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RouteDeleteOne, by_user_id=current_user.id)
        return Success(msg="Deleted Successfully", data={"deleted_id": route_id})
    return Success(msg="Route not found", data=None)
