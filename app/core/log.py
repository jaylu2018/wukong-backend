import sys
from typing import Optional

from loguru import logger as loguru_logger

from app.core.config import APP_SETTINGS
from app.core.context_vars import trace_id_var, user_id_var
from app.models import Log
from app.models.base import LogType, LogDetailType


class Logging:
    def __init__(self) -> None:
        debug = APP_SETTINGS.DEBUG
        self.level = "DEBUG" if debug else "INFO"

    def setup_logger(self):
        loguru_logger.remove()
        # 自定义日志格式，包含 trace_id
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "trace_id={extra[trace_id]} - "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
        loguru_logger.add(
            sys.stdout,
            level=self.level,
            format=log_format
        )
        loguru_logger.add(
            "app.log",
            rotation="10 MB",
            level=self.level,
            format=log_format
        )
        return loguru_logger


async def insert_log(
        log_type: LogType,
        log_detail_type: LogDetailType,
        detail: Optional[str] = None,
        stack_trace: Optional[str] = None,
):
    trace_id = trace_id_var.get()
    by_user_id = user_id_var.get()
    print(by_user_id, trace_id)
    await Log.create(
        log_type=log_type,
        log_detail_type=log_detail_type,
        by_user_id=by_user_id,
        trace_id=trace_id,
        detail=detail,
        stack_trace=stack_trace
    )


logging = Logging()
logger = logging.setup_logger()
logger = logger.bind(trace_id=None)
