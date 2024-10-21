from fastapi import APIRouter

from app.api.base import BaseCRUDRouter
from app.models import User, Log
from app.models.base import LogType, LogDetailType
from app.services.log import log_service
from app.schemas.logs import LogUpdate, BaseLog

# 定义日志详细类型
log_detail_types = {
    "list": LogDetailType.LogGetList,
    "retrieve": LogDetailType.LogGetOne,
    "update": LogDetailType.LogUpdate,
    "delete": LogDetailType.LogDelete,
    "batch_delete": LogDetailType.LogBatchDelete,
}


class LogCRUDRouter(BaseCRUDRouter[Log, BaseLog, LogUpdate, User]):
    def _add_routes(self):
        super()._add_routes()


# 创建路由器实例
router = APIRouter()
log_router = LogCRUDRouter(
    model=Log,
    create_schema=BaseLog,
    update_schema=LogUpdate,
    service=log_service,
    log_detail_types=log_detail_types,
    prefix="/logs",
    tags=["日志管理"],
    log_type=LogType.AdminLog,
    pk="pk",
)

router.include_router(log_router.router)
