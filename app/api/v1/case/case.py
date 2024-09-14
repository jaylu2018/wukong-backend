# from fastapi import APIRouter, Depends, Query
# from typing import List
#
# from app.models import User
# from app.models.base import LogType, LogDetailType
# from app.services.case import case_service
# from app.services.log import log_service
# from app.schemas.base import Success, SuccessExtra
# from app.schemas.case import CaseCreate, CaseUpdate, CaseOut
# from app.core.auth import get_current_user
#
# router = APIRouter()
#
#
# @router.get("/cases", summary="获取案例列表")
# async def get_cases(
#         current: int = Query(1, description="页码"),
#         size: int = Query(10, description="每页数量"),
#         current_user: User = Depends(get_current_user)
# ):
#     total, cases = await case_service.get_cases(page=current, page_size=size)
#     await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.CaseGetList, by_user_id=current_user.id)
#     return SuccessExtra(data=[CaseOut.model_validate(case) for case in cases], total=total, current=current, size=size)
#
#
# @router.get("/cases/{case_id}", response_model=Success[CaseOut], summary="获取单个案例")
# async def get_case(case_id: int, current_user: User = Depends(get_current_user)):
#     case = await case_service.get_case(case_id)
#     await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.CaseGetOne, by_user_id=current_user.id)
#     if case:
#         return Success(data=CaseOut.model_validate(case))
#     return Success(msg="Case not found", data=None)
#
#
# @router.post("/cases", response_model=Success[CaseOut], summary="创建案例")
# async def create_case(case_in: CaseCreate, current_user: User = Depends(get_current_user)):
#     new_case = await case_service.create_case(case_in)
#     await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.CaseCreateOne, by_user_id=current_user.id)
#     return Success(msg="Created Successfully", data=CaseOut.model_validate(new_case))
#
#
# @router.patch("/cases/{case_id}", response_model=Success[CaseOut], summary="更新案例")
# async def update_case(case_id: int, case_in: CaseUpdate, current_user: User = Depends(get_current_user)):
#     updated_case = await case_service.update_case(case_id, case_in)
#     await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.CaseUpdateOne, by_user_id=current_user.id)
#     if updated_case:
#         return Success(msg="Updated Successfully", data=CaseOut.model_validate(updated_case))
#     return Success(msg="Case not found", data=None)
#
#
# @router.delete("/cases/{case_id}", response_model=Success, summary="删除案例")
# async def delete_case(case_id: int, current_user: User = Depends(get_current_user)):
#     deleted = await case_service.delete_case(case_id)
#     await log_service.create(log_type=LogType.AdminLog, log_detail_type=LogDetailType.CaseDeleteOne, by_user_id=current_user.id)
#     if deleted:
#         return Success(msg="Deleted Successfully", data={"deleted_id": case_id})
#     return Success(msg="Case not found", data=None)
