from fastapi import APIRouter, Query, Depends, HTTPException
from tortoise.expressions import Q

from app.core.auth import get_current_user
from app.models import User
from app.models.base import LogType, LogDetailType
from app.services.user import user_service
from app.services.log import log_service
from app.schemas.base import Success, SuccessExtra
from app.schemas.users import UserCreate, UserUpdate

router = APIRouter()


@router.get("/users", summary="查看用户列表")
async def get_users(
        current: int = Query(1, description="页码"),
        size: int = Query(10, description="每页数量"),
        user_name: str = Query(None, description="用户名"),
        user_gender: str = Query(None, description="用户性别"),
        nick_name: str = Query(None, description="用户昵称"),
        user_phone: str = Query(None, description="用户手机"),
        user_email: str = Query(None, description="用户邮箱"),
        status: str = Query(None, description="用户状态"),
        current_user: User = Depends(get_current_user)
):
    search_params = {
        "user_name__contains": user_name,
        "user_gender__contains": user_gender,
        "nick_name__contains": nick_name,
        "user_phone__contains": user_phone,
        "user_email__contains": user_email,
        "status__contains": status
    }
    search_query = Q(**{k: v for k, v in search_params.items() if v is not None})
    total, user_objs = await user_service.list(page=current, page_size=size, search=search_query, order=["id"])
    records = [await user_service.to_dict_with_roles(user_obj) for user_obj in user_objs]
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserGetList, by_user_id=current_user.id)
    return SuccessExtra(data={"records": records}, total=total, current=current, size=size)


@router.get("/users/{user_id}", summary="查看用户")
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    user_obj = await user_service.get(id=user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = await user_service.to_dict_with_roles(user_obj)
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserGetOne, by_user_id=current_user.id)
    return Success(data=user_data)


@router.post("/users", response_model=Success[dict], summary="创建用户")
async def create_user(user_in: UserCreate, current_user: User = Depends(get_current_user)):
    new_user = await user_service.create(obj_in=user_in)
    await user_service.update_roles_by_code(new_user, user_in.roles)
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserCreateOne, by_user_id=current_user.id)
    return Success(msg="Created Successfully", data={"created_id": new_user.id})


@router.patch("/users/{user_id}", response_model=Success[dict], summary="更新用户")
async def update_user(user_id: int, user_in: UserUpdate, current_user: User = Depends(get_current_user)):
    user = await user_service.update(user_id=user_id, obj_in=user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_service.update_roles_by_code(user, user_in.roles)
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserUpdateOne, by_user_id=current_user.id)
    return Success(msg="Updated Successfully", data={"updated_id": user_id})


@router.delete("/users/{user_id}", response_model=Success[dict], summary="删除用户")
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    deleted = await user_service.remove(id=user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_id": user_id})


@router.delete("/users", response_model=Success[dict], summary="批量删除用户")
async def batch_delete_users(ids: str = Query(..., description="用户ID列表, 用逗号隔开"), current_user: User = Depends(get_current_user)):
    user_ids = [int(user_id) for user_id in ids.split(",")]
    deleted_ids = await user_service.batch_remove(user_ids)

    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserBatchDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_ids": deleted_ids})
