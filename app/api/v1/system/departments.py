import time

from fastapi import APIRouter, Request
from typing import List

from app.api.base import BaseCRUDRouter
from app.core.log import insert_log
from app.models import User
from app.models.department import Department
from app.models.base import LogType, LogDetailType
from app.schemas.departments import DepartmentOut, DepartmentCreate, DepartmentUpdate, DepartmentSearch
from app.services.department import department_service
from app.schemas.base import ResponseList, Response

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.DepartmentGetList,
    "retrieve": LogDetailType.DepartmentGetOne,
    "create": LogDetailType.DepartmentCreateOne,
    "update": LogDetailType.DepartmentUpdateOne,
    "delete": LogDetailType.DepartmentDeleteOne,
    "batch_delete": LogDetailType.DepartmentBatchDeleteOne,
    "get_tree": LogDetailType.DepartmentGetTree,
}


class DepartmentCRUDRouter(BaseCRUDRouter[Department, DepartmentCreate, DepartmentUpdate, User]):
    def _add_routes(self):
        # 获取部门树形结构
        @self.router.get("/tree/", summary="获取部门树形结构", response_model=Response[List[DepartmentOut]])
        async def get_department_tree(request: Request):
            start_time = time.time()
            try:
                query_params = dict(request.query_params)
                _, departments = await self.service.list()
                schema_fields = {field.alias: field_name for field_name, field in DepartmentSearch.model_fields.items() if field.alias}
                filters = {schema_fields.get(key, key): value for key, value in query_params.items()}
                filtered_departments = [
                    department for department in departments
                    if all(
                        value in getattr(department, key, "") if key == "name" else getattr(department, key, None) == value
                        for key, value in filters.items()
                    )
                ]
                department_tree = await self.service.get_departments_tree(filtered_departments)
                if not department_tree and filtered_departments:
                    department_list = [await self.service.to_dict(department) for department in filtered_departments]
                    return Response(data=department_list)
                return Response(data=department_tree)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_tree"], detail=f"请求耗时 {duration:.2f} 秒")

        # 重用父类的方法（获取列表、获取单个、创建、更新、删除、批量删除）
        super()._add_routes()


# 创建路由器实例
router = APIRouter()
department_router = DepartmentCRUDRouter(
    model=Department,
    create_schema=DepartmentCreate,
    update_schema=DepartmentUpdate,
    service=department_service,
    log_detail_types=log_detail_types,
    prefix="/departments",
    tags=["部门管理"],
    log_type=LogType.AdminLog,
    pk='pk',
    list_response_model=ResponseList[List[DepartmentOut]]
)

router.include_router(department_router.router)
