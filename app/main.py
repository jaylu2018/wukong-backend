import time

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import api_router
from app.core.exceptions import value_error_handler, global_exception_handler
from app.core.log import insert_log, logger
from app.utils.public import refresh_api_list
from app.core.settings import APP_SETTINGS
from app.core.migrate import migrate_db
from app.core.middleware import register_middlewares
from app.models.base import LogType, LogDetailType


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_time = time.time()
    try:
        await migrate_db()
        await refresh_api_list()

        await insert_log(log_type=LogType.SystemLog, log_detail_type=LogDetailType.SystemStart)
        yield
    finally:
        end_time = time.time()
        runtime = end_time - start_time
        logger.info(f"App {_app.title} runtime: {runtime} seconds")  # noqa
        await insert_log(log_type=LogType.SystemLog, log_detail_type=LogDetailType.SystemStop)


app = FastAPI(
    title=APP_SETTINGS.APP_TITLE,
    description=APP_SETTINGS.APP_DESCRIPTION,
    version=APP_SETTINGS.VERSION,
    openapi_url="/openapi.json",
    middleware=register_middlewares(),
    lifespan=lifespan
)

# 注册路由
app.include_router(api_router, prefix='/api')

# 先注册具体的异常处理器
app.add_exception_handler(ValueError, value_error_handler)
# 然后注册全局的异常处理器
app.add_exception_handler(Exception, global_exception_handler)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9997, reload=True, access_log=False)
