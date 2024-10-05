import time

from fastapi import APIRouter, Depends

from app.api.base import BaseCRUDRouter
from app.core.dependency import get_current_user
from app.models import User, Role
from app.models.base import LogType, LogDetailType
from app.services.role import role_service
from app.schemas.base import Response
from app.schemas.roles import RoleCreate, RoleUpdate, RoleUpdateAuthorization
from app.core.log import insert_log

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.RoleGetList,
    "retrieve": LogDetailType.RoleGetOne,
    "create": LogDetailType.RoleCreateOne,
    "update": LogDetailType.RoleUpdateOne,
    "delete": LogDetailType.RoleDeleteOne,
    "batch_delete": LogDetailType.RoleBatchDelete,
    "get_menus": LogDetailType.RoleGetMenus,
    "update_menus": LogDetailType.RoleUpdateMenus,
}


class RoleCRUDRouter(BaseCRUDRouter[Role, RoleCreate, RoleUpdate, User]):
    def _add_routes(self):
        # 重用父类的方法（获取列表、获取单个、创建、更新、删除、批量删除）
        super()._add_routes()

        # 获取角色的菜单
        @self.router.get(f"/{{{self.pk}}}/menus", summary="查看角色菜单")
        async def get_role_menus(
                pk: int,
                current_user: User = Depends(self.get_current_user)
        ):
            start_time = time.time()
            try:
                role_home, menu_ids = await self.service.get_role_menus(pk)
                data = {"roleHome": role_home, "menuIds": menu_ids}
                return Response(data=data)
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["get_menus"], detail=f"请求耗时 {duration:.2f} 秒")

        # 更新角色的菜单
        @self.router.patch(f"/{{{self.pk}}}/menus", summary="更新角色菜单")
        async def update_role_menus(
                pk: int,
                role_in: RoleUpdateAuthorization,
                current_user: User = Depends(self.get_current_user)
        ):
            start_time = time.time()
            try:
                updated_role = await self.service.update_menus(pk, role_in)
                return Response(
                    msg="更新成功",
                    data={
                        "updated_menu_ids": role_in.menu_ids,
                        "updated_role_home": updated_role.role_home
                    }
                )
            finally:
                duration = time.time() - start_time
                await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["update_menus"], detail=f"请求耗时 {duration:.2f} 秒")


# 创建路由器实例
router = APIRouter()
role_router = RoleCRUDRouter(
    model=Role,
    create_schema=RoleCreate,
    update_schema=RoleUpdate,
    service=role_service,
    log_detail_types=log_detail_types,
    get_current_user=get_current_user,
    prefix="/roles",
    tags=["角色管理"],
    log_type=LogType.AdminLog,
    pk="pk",
    unique_fields=["role_code"],
)

router.include_router(role_router.router)
