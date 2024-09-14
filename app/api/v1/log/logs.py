from fastapi import APIRouter, Query, Depends
from tortoise.expressions import Q

from app.core.auth import get_current_user
from app.models.system import User, LogType, LogDetailType
from app.services.log import log_service
from app.schemas.base import Success, SuccessExtra
from app.schemas.logs import LogUpdate

router = APIRouter()


@router.get("/logs", summary="查看日志列表")
async def get_logs(
        current: int = Query(1, description="页码"),
        size: int = Query(10, description="每页数量"),
        log_type: str = Query(None, description="日志类型"),
        log_detail_type: str = Query(None, description="日志详细类型"),
        current_user: User = Depends(get_current_user)
):
    q = Q()
    if log_type:
        q &= Q(log_type=log_type)
    if log_detail_type:
        q &= Q(log_detail_type=log_detail_type)

    total, log_objs = await log_service.list(page=current, page_size=size, search=q, order=["-id"])
    records = [await log_service.to_dict(log) for log in log_objs]
    data = {"records": records}
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogGetList, by_user_id=current_user.id)
    return SuccessExtra(data=data, total=total, current=current, size=size)


@router.get("/logs/{log_id}", summary="查看日志")
async def get_log(log_id: int, current_user: User = Depends(get_current_user)):
    log_obj = await log_service.get(id=log_id)
    data = await log_service.to_dict(log_obj, exclude_fields=["id", "create_time", "update_time"])
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogGetOne, by_user_id=current_user.id)
    return Success(data=data)


@router.patch("/logs/{log_id}", summary="更新日志")
async def update_log(log_id: int, log_in: LogUpdate, current_user: User = Depends(get_current_user)):
    await log_service.update(log_id=log_id, obj_in=log_in.model_dump())
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogUpdate, by_user_id=current_user.id)
    return Success(msg="Update Successfully")


@router.delete("/logs/{log_id}", summary="删除日志")
async def delete_log(log_id: int, current_user: User = Depends(get_current_user)):
    await log_service.remove(id=log_id)
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogDelete, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_id": log_id})


@router.delete("/logs", summary="批量删除日志")
async def batch_delete_logs(ids: str = Query(..., description="日志ID列表, 用逗号隔开"), current_user: User = Depends(get_current_user)):
    log_ids = ids.split(",")
    deleted_ids = []
    for log_id in log_ids:
        await log_service.remove(id=int(log_id))
        deleted_ids.append(int(log_id))
    await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogBatchDelete, by_user_id=current_user.id)
    return Success(msg="Deleted Successfully", data={"deleted_ids": deleted_ids})
