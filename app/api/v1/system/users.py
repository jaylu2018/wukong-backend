from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.core.dependency import get_current_user
from app.models import User
from app.models.base import LogType, LogDetailType
from app.schemas.base import Success, SuccessExtra
from app.schemas.users import UserCreate, UserOut, UserUpdate
from app.services.log import log_service
from app.services.user import user_service
from app.utils.public import insert_log

router = APIRouter()


@router.get("/users", summary="查看用户列表", response_model=SuccessExtra[List[UserOut]])
async def get_users(
        current: int = Query(1, description="页码"),
        size: int = Query(10, description="每页数量"),
        user_name: Optional[str] = Query(None, description="用户名"),
        user_gender: Optional[str] = Query(None, description="用户性别"),
        nick_name: Optional[str] = Query(None, description="用户昵称"),
        user_phone: Optional[str] = Query(None, description="用户手机"),
        user_email: Optional[str] = Query(None, description="用户邮箱"),
        status: Optional[str] = Query(None, description="用户状态"),
        current_user: User = Depends(get_current_user),
):
    search_params = {
        "user_name__contains": user_name,
        "user_gender": user_gender,
        "nick_name__contains": nick_name,
        "user_phone__contains": user_phone,
        "user_email__contains": user_email,
        "status": status,
    }
    filters = {k: v for k, v in search_params.items() if v is not None}
    total, user_objs = await user_service.list_users(page=current, page_size=size, filters=filters)
    records = [await user_service.to_dict_with_roles(user) for user in user_objs]
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserGetList, by_user_id=current_user.id)
    return SuccessExtra(data=records, total=total, current=current, size=size)


@router.get("/users/{user_id}", summary="查看用户", response_model=Success[UserOut])
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    user_obj = await user_service.get_user_by_id(user_id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = await user_service.to_dict_with_roles(user_obj)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserGetOne, by_user_id=current_user.id)
    return Success(data=user_data)


@router.post("/users", summary="创建用户", response_model=Success[dict])
async def create_user(user_in: UserCreate, current_user: User = Depends(get_current_user)):
    new_user = await user_service.create_user(user_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserCreateOne, by_user_id=current_user.id)
    return Success(msg="Created Successfully", data={"created_id": new_user.id})


@router.patch("/users/{user_id}", summary="更新用户", response_model=Success[dict])
async def update_user(user_id: int, user_in: UserUpdate, current_user: User = Depends(get_current_user)):
    user = await user_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserUpdateOne, by_user_id=current_user.id)
    return Success(msg="Updated Successfully", data={"updated_id": user_id})


@router.delete("/users/{user_id}", summary="删除用户", response_model=Success[dict])
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_id": user_id})


@router.delete("/users", summary="批量删除用户", response_model=Success[dict])
async def batch_delete_users(ids: str = Query(..., description="用户ID列表, 用逗号隔开"), current_user: User = Depends(get_current_user)):
    user_ids = [int(user_id.strip()) for user_id in ids.split(",") if user_id.strip().isdigit()]
    deleted_ids = await user_service.batch_delete_users(user_ids)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.UserBatchDeleteOne, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_ids": deleted_ids})
