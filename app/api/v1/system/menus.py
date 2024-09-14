from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List

from app.api.v1.utils import insert_log
from app.models import Menu, User
from app.models.base import LogType, LogDetailType
from app.services.menu import menu_service
from app.schemas.base import Success, SuccessExtra
from app.schemas.menus import MenuCreate, MenuUpdate
from app.core.auth import get_current_user

router = APIRouter()


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
                menu_dict = await menu.to_dict()
                menu_dict["buttons"] = [await button.to_dict() for button in await menu.buttons]
            if children:
                menu_dict["children"] = children
            tree.append(menu_dict)
    return tree


@router.get("/menus", summary="查看用户菜单")
async def get_menus(
        current: int = Query(1, description="页码"),
        size: int = Query(100, description="每页数量"),
        current_user: User = Depends(get_current_user)
):
    total, menus = await menu_service.list(page=current, page_size=size, order=["id"])
    menu_tree = await build_menu_tree(menus, simple=False)
    data = {"records": menu_tree}
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuGetList, by_user_id=current_user.id)
    return SuccessExtra(data=data, total=total, current=current, size=size)


@router.get("/menus/tree/", summary="查看菜单树")
async def get_menu_tree(current_user: User = Depends(get_current_user)):
    menus = await menu_service.get_non_constant_menus()
    menu_tree = await build_menu_tree(menus, simple=True)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuGetTree, by_user_id=current_user.id)
    return Success(data=menu_tree)


@router.get("/menus/{menu_id}", summary="查看菜单")
async def get_menu(menu_id: int, current_user: User = Depends(get_current_user)):
    menu = await menu_service.get(id=menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuGetOne, by_user_id=current_user.id)
    return Success(data=await menu.to_dict())


@router.post("/menus", summary="创建菜单")
async def create_menu(menu_in: MenuCreate, current_user: User = Depends(get_current_user)):
    new_menu = await menu_service.create(menu_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuCreateOne, by_user_id=current_user.id)
    return Success(msg="Created Successfully", data={"created_id": new_menu.id})


@router.patch("/menus/{menu_id}", summary="更新菜单")
async def update_menu(menu_id: int, menu_in: MenuUpdate, current_user: User = Depends(get_current_user)):
    updated_menu = await menu_service.update(menu_id, menu_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuUpdateOne, by_user_id=current_user.id)
    return Success(msg="Updated Successfully", data={"updated_id": menu_id})


@router.delete("/menus/{menu_id}", summary="删除菜单")
async def delete_menu(menu_id: int, current_user: User = Depends(get_current_user)):
    await menu_service.remove(menu_id)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_id": menu_id})


@router.delete("/menus", summary="批量删除菜单")
async def batch_delete_menus(ids: str = Query(description="菜单ID列表, 用逗号隔开"), current_user: User = Depends(get_current_user)):
    menu_ids = [int(id) for id in ids.split(",")]
    await menu_service.batch_remove(menu_ids)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuBatchDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_ids": menu_ids})


@router.get("/menus/pages/", summary="查看一级菜单")
async def get_first_level_menus(current_user: User = Depends(get_current_user)):
    menus = await menu_service.get_first_level_menus()
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuGetPages, by_user_id=current_user.id)
    return Success(data=[menu.route_name for menu in menus])


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


@router.get("/menus/buttons/tree/", summary="查看菜单按钮树")
async def get_menu_button_tree(current_user: User = Depends(get_current_user)):
    menus_with_button = await menu_service.get_menus_with_buttons()
    menu_objs = menus_with_button.copy()
    while len(menus_with_button) > 0:
        menu = menus_with_button.pop()
        if menu.parent_id != 0:
            menu = await menu_service.get(id=menu.parent_id)
            menus_with_button.append(menu)
        else:
            menu_objs.append(menu)

    menu_objs = list(set(menu_objs))
    data = []
    if menu_objs:
        data = await build_menu_button_tree(menu_objs)

    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.MenuGetButtonsTree, by_user_id=current_user.id)
    return Success(data=data)
