from fastapi import APIRouter

from .auth import router_auth
from .log import router_log
from .route import router_route
from .system import router_system

v1_router = APIRouter()

v1_router.include_router(router_auth, prefix="/auth", tags=["权限认证"])
v1_router.include_router(router_log, prefix="/log", tags=["日志管理"])
v1_router.include_router(router_route, prefix="/route", tags=["路由管理"])
v1_router.include_router(router_system, prefix="/system")
