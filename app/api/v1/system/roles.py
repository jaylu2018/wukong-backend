from typing import Optional

from fastapi import APIRouter, Query, Depends, HTTPException
from tortoise.expressions import Q

from app.core.dependency import get_current_user
from app.models import User, Role
from app.models.base import LogType, LogDetailType
from app.services.role import role_service
from app.services.log import log_service
from app.schemas.base import Success, SuccessExtra
from app.schemas.roles import RoleCreate, RoleUpdate, RoleUpdateAuthrization
from app.utils.public import insert_log

router = APIRouter()


@router.get("/roles", summary="查看角色列表")
async def get_roles(
        current: int = Query(1, description="页码"),
        size: int = Query(10, description="每页数量"),
        role_name: Optional[str] = Query(None, description="角色名称"),
        role_code: Optional[str] = Query(None, description="角色编码"),
        current_user: User = Depends(get_current_user)
):
    search_params = {
        "role_name__contains": role_name,
        "role_code__contains": role_code,
    }
    filters = {k: v for k, v in search_params.items() if v is not None}
    total, role_objs = await role_service.list(page=current, page_size=size, order=["id"], **filters)
    records = [await role_service.to_dict(role) for role in role_objs]
    data = {"records": records}
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleGetList, by_user_id=current_user.id)
    return SuccessExtra(data=data, total=total, current=current, size=size)


@router.get("/roles/{role_id}", summary="查看角色")
async def get_role(role_id: int, current_user: User = Depends(get_current_user)):
    role_obj = await role_service.get(id=role_id)
    if not role_obj:
        raise HTTPException(status_code=404, detail="Role not found")
    data = await role_service.to_dict(role_obj)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleGetOne, by_user_id=current_user.id)
    return Success(data=data)


@router.post("/roles", summary="创建角色")
async def create_role(role_in: RoleCreate, current_user: User = Depends(get_current_user)):
    role = await Role.get_or_none(role_code=role_in.role_code)
    if role:
        raise HTTPException(status_code=409, detail="The role with this code already exists in the system.")
    new_role = await role_service.create(obj_in=role_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleCreateOne, by_user_id=current_user.id)
    return Success(msg="Created Successfully", data={"created_id": new_role.id})


@router.patch("/roles/{role_id}", summary="更新角色")
async def update_role(role_id: int, role_in: RoleUpdate, current_user: User = Depends(get_current_user)):
    role = await role_service.update(role_id=role_id, obj_in=role_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleUpdateOne, by_user_id=current_user.id)
    return Success(msg="Updated Successfully", data={"updated_id": role_id})


@router.delete("/roles/{role_id}", summary="删除角色")
async def delete_role(role_id: int, current_user: User = Depends(get_current_user)):
    await role_service.remove(id=role_id)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_id": role_id})


@router.delete("/roles", summary="批量删除角色")
async def batch_delete_roles(ids: str = Query(..., description="角色ID列表, 用逗号隔开"), current_user: User = Depends(get_current_user)):
    role_ids = ids.split(",")
    deleted_ids = []
    for role_id in role_ids:
        await role_service.remove(id=int(role_id))
        deleted_ids.append(int(role_id))
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleBatchDelete, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_ids": deleted_ids})


@router.get("/roles/{role_id}/menus", summary="查看角色菜单")
async def get_role_menus(role_id: int, current_user: User = Depends(get_current_user)):
    role_home, menu_ids = await role_service.get_role_menus(role_id)
    data = {"roleHome": role_home, "menuIds": menu_ids}
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleGetMenus, by_user_id=current_user.id)
    return Success(data=data)


@router.patch("/roles/{role_id}/menus", summary="更新角色菜单")
async def update_role_menus(role_id: int, role_in: RoleUpdateAuthrization, current_user: User = Depends(get_current_user)):
    updated_role = await role_service.update_menus(role_id, role_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.RoleUpdateMenus, by_user_id=current_user.id)
    return Success(msg="Updated Successfully", data={"updated_menu_ids": role_in.menu_ids, "updated_role_home": updated_role.role_home})
