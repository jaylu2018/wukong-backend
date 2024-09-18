from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependency import get_current_user
from app.models import Api, User
from app.models.base import LogDetailType, LogType, StatusType
from app.schemas.apis import ApiCreate, ApiUpdate, ApiOut
from app.schemas.base import Success, SuccessExtra
from app.services.apis import api_service
from app.core.log import insert_log

router = APIRouter()


@router.get("/apis", summary="获取 API 列表", response_model=SuccessExtra[List[ApiOut]])
async def get_apis(
        current: int = Query(1, description="页码"),
        size: int = Query(10, description="每页数量"),
        path: Optional[str] = Query(None, description="API 路径"),
        summary: Optional[str] = Query(None, description="API 简介"),
        tags: Optional[str] = Query(None, description="API 标签，使用 '|' 分隔"),
        status: Optional[StatusType] = Query(None, description="API 状态"),
        current_user: User = Depends(get_current_user),
):
    search_params = {
        "path__contains": path,
        "summary__contains": summary,
        "tags__contains": tags,
        "status": status,
    }
    filters = {k: v for k, v in search_params.items() if v is not None}

    user_roles = await current_user.roles.all()
    is_superuser = any(role.role_code == "R_SUPER" for role in user_roles)

    if is_superuser:
        total, apis = await api_service.list(page=current, page_size=size, order=["tags", "id"], **filters)
    else:
        api_ids = set()
        for role in user_roles:
            role_apis = await role.apis.all()
            api_ids.update(api.id for api in role_apis)
        total = len(api_ids)
        apis = (
            await Api.filter(id__in=api_ids)
            .filter(filters)
            .offset((current - 1) * size)
            .limit(size)
            .order_by("tags", "id")
        )

    records = [await api_service.to_dict(api) for api in apis]
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiGetList)
    return SuccessExtra(data=records, total=total, current=current, size=size)


@router.get("/apis/{api_id}", summary="查看API详情", response_model=Success[ApiOut])
async def get_api(api_id: int, current_user: User = Depends(get_current_user)):
    api_obj = await api_service.get(api_id)
    if not api_obj:
        raise HTTPException(status_code=404, detail="API未找到")
    data = await api_service.to_dict(api_obj)
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiGetOne)
    return Success(data=data)


@router.post("/apis", summary="创建API", response_model=Success[dict])
async def create_api(
        api_in: ApiCreate, current_user: User = Depends(get_current_user)
):
    new_api = await api_service.create(api_in)
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiCreateOne)
    return Success(msg="创建成功", data={"created_id": new_api.id})


@router.patch("/apis/{api_id}", summary="更新API", response_model=Success[dict])
async def update_api(
        api_id: int, api_in: ApiUpdate, current_user: User = Depends(get_current_user)
):
    updated_api = await api_service.update(api_id, api_in)
    if not updated_api:
        raise HTTPException(status_code=404, detail="API未找到")
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiUpdateOne)
    return Success(msg="更新成功", data={"updated_id": api_id})


@router.delete("/apis/{api_id}", summary="删除API", response_model=Success[dict])
async def delete_api(api_id: int, current_user: User = Depends(get_current_user)):
    deleted = await api_service.remove(api_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="API未找到")
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiDeleteOne)
    return Success(msg="删除成功", data={"deleted_id": api_id})


@router.delete("/apis", summary="批量删除API", response_model=Success[dict])
async def batch_delete_apis(
        ids: str = Query(..., description="API ID列表，用逗号隔开"),
        current_user: User = Depends(get_current_user),
):
    api_ids = [int(api_id.strip()) for api_id in ids.split(",") if api_id.strip().isdigit()]
    deleted_ids = await api_service.batch_remove(api_ids)
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiBatchDelete)
    return Success(msg="批量删除成功", data={"deleted_ids": deleted_ids})


@router.get("/apis/tree/", summary="获取API树形结构", response_model=Success[List[dict]])
async def get_api_tree(current_user: User = Depends(get_current_user)):
    api_tree = await api_service.get_api_tree()
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.ApiGetTree)
    return Success(data=api_tree)
