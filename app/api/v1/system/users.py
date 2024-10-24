import time

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.api.base import BaseCRUDRouter
from app.models import User
from app.models.base import LogType, LogDetailType
from app.schemas.base import Response, ResponseList
from app.schemas.users import UserCreate, UserOut, UserUpdate
from app.services.user import user_service
from app.core.log import insert_log

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.UserGetList,
    "retrieve": LogDetailType.UserGetOne,
    "create": LogDetailType.UserCreateOne,
    "update": LogDetailType.UserUpdateOne,
    "delete": LogDetailType.UserDeleteOne,
    "batch_delete": LogDetailType.UserBatchDelete,
}


class UserCRUDRouter(BaseCRUDRouter[User, UserCreate, UserUpdate, User]):
    def _add_routes(self):

        # 重写列表查询，添加自定义过滤逻辑和返回角色信息
        @self.router.get("", summary="查看用户列表", response_model=ResponseList[List[UserOut]])
        async def list_items(
                page: int = Query(1, description="页码"),
                size: int = Query(10, description="每页数量"),
                user_name: Optional[str] = Query(None, description="用户名"),
                user_gender: Optional[str] = Query(None, description="用户性别"),
                nick_name: Optional[str] = Query(None, description="用户昵称"),
                user_phone: Optional[str] = Query(None, description="用户手机"),
                user_email: Optional[str] = Query(None, description="用户邮箱"),
                status: Optional[str] = Query(None, description="用户状态"),
                department_id: Optional[int] = Query(None, description="部门ID"),
        ):
            start_time = time.time()
            try:
                search_params = {
                    "user_name__contains": user_name,
                    "user_gender": user_gender,
                    "nick_name__contains": nick_name,
                    "user_phone__contains": user_phone,
                    "user_email__contains": user_email,
                    "status": status,
                    "department_id": department_id,
                }
                filters = {k: v for k, v in search_params.items() if v is not None}
                total, user_objs = await self.service.list(page=page, size=size, **filters)
                records = [await self.service.to_dict_with_roles(user) for user in user_objs]
                return ResponseList(data={"list": records, "total": total, "current": page, "size": size})
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["list"], detail=f"请求耗时 {duration:.2f} 秒")

        # 重写获取单个用户，返回包含角色信息的数据
        @self.router.get(f"/{{{self.pk}}}", summary="查看用户", response_model=Response[UserOut])
        async def get_item(
                pk: int,
        ):
            start_time = time.time()
            try:
                user_obj = await self.service.get(id=pk)
                if not user_obj:
                    raise HTTPException(status_code=404, detail="User not found")
                user_data = await self.service.to_dict_with_roles(user_obj)
                return Response(data=user_data)
            finally:
                duration = time.time() - start_time
                await insert_log(
                    log_type=self.log_type,
                    log_detail_type=self.log_detail_types["retrieve"],
                    detail=f"请求耗时 {duration:.2f} 秒"
                )

        # 重用父类的方法
        super()._add_routes()


# 创建路由器实例
router = APIRouter()
user_router = UserCRUDRouter(
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    service=user_service,
    log_detail_types=log_detail_types,
    prefix="/users",
    tags=["用户管理"],
    log_type=LogType.AdminLog,
    pk="pk",
)

router.include_router(user_router.router)
