import logging
import sys
from typing import Optional

from loguru import logger

from app.core.context_vars import trace_id_var, user_id_var
from app.models import Log
from app.models.base import LogType, LogDetailType

# 定义日志格式
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level}</level> | "
    "trace_id={extra[trace_id]} - "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

# 移除默认的日志处理器
logger.remove()

# 在应用启动时，全局绑定默认的 trace_id
logger = logger.bind(trace_id="N/A")

# 添加新的日志处理器
logger.add(
    sys.stdout,
    level="INFO",
    format=log_format,
    enqueue=True,
    backtrace=True,
    diagnose=True,
)


# 定义拦截器，将 logging 模块的日志转发到 Loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取 Loguru 等效的日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 获取调用者的代码位置
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 绑定 trace_id
        log_record = logger.bind(trace_id=record.__dict__.get("trace_id", "N/A"))
        log_record.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


# 配置 logging 模块，使用自定义的拦截器
logging.root.handlers = [InterceptHandler()]
logging.root.setLevel(0)

# 拦截特定的日志记录器
logging_loggers = [
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "fastapi",
]

for logger_name in logging_loggers:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler()]
    logging_logger.propagate = False


async def insert_log(
        log_type: LogType,
        log_detail_type: LogDetailType,
        detail: Optional[str] = None,
        stack_trace: Optional[str] = None,
):
    trace_id = trace_id_var.get()
    by_user_id = user_id_var.get()
    await Log.create(
        log_type=log_type,
        log_detail_type=log_detail_type,
        by_user_id=by_user_id,
        trace_id=trace_id,
        detail=detail,
        stack_trace=stack_trace
    )
    logger.bind(trace_id=trace_id or "N/A").info(
        f"LogType: {log_type}, LogDetailType: {log_detail_type}, "
        f"by_user_id: {by_user_id}, trace_id: {trace_id}, "
        f"detail: {detail}, stack_trace: {stack_trace}"
    )
