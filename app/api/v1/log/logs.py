from fastapi import APIRouter, Query, Depends

from app.core.dependency import get_current_user
from app.models import User
from app.models.base import LogType, LogDetailType
from app.services.log import log_service
from app.schemas.base import Success, SuccessExtra
from app.schemas.logs import LogUpdate
from app.core.log import insert_log

router = APIRouter()


@router.get("/logs", summary="查看日志列表")
async def get_logs(
        current: int = Query(1, description="页码"),
        size: int = Query(10, description="每页数量"),
        log_type: str = Query(None, description="日志类型"),
        log_detail_type: str = Query(None, description="日志详细类型"),
):
    search_params = {
        "log_type": log_type,
        "log_detail_type": log_detail_type,
    }
    filters = {k: v for k, v in search_params.items() if v is not None}
    total, log_objs = await log_service.list(page=current, page_size=size, order=["-id"], **filters)
    records = [await log_service.to_dict(log, exclude_fields=["by_user", "api_log"]) for log in log_objs]
    data = {"records": records}
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogGetList)
    return SuccessExtra(data=data, total=total, current=current, size=size)


@router.get("/logs/{log_id}", summary="查看日志")
async def get_log(log_id: int, current_user: User = Depends(get_current_user)):
    log_obj = await log_service.get(id=log_id)
    data = await log_service.to_dict(log_obj, exclude_fields=["by_user", "api_log"])
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogGetOne)
    return Success(data=data)


@router.patch("/logs/{log_id}", summary="更新日志")
async def update_log(log_id: int, log_in: LogUpdate, current_user: User = Depends(get_current_user)):
    await log_service.update(log_id, log_in)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogUpdate)
    return Success(msg="Update Successfully")


@router.delete("/logs/{log_id}", summary="删除日志")
async def delete_log(log_id: int, current_user: User = Depends(get_current_user)):
    await log_service.remove(id=log_id)
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogDelete)
    return Success(msg="Deleted Successfully", data={"deleted_id": log_id})


@router.delete("/logs", summary="批量删除日志")
async def batch_delete_logs(ids: str = Query(..., description="日志ID列表, 用逗号隔开"), current_user: User = Depends(get_current_user)):
    log_ids = ids.split(",")
    deleted_ids = []
    for log_id in log_ids:
        await log_service.remove(id=int(log_id))
        deleted_ids.append(int(log_id))
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.LogBatchDelete)
    return Success(msg="Deleted Successfully", data={"deleted_ids": deleted_ids})
