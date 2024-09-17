import time

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from loguru import logger
from contextlib import asynccontextmanager

from app.api import api_router
from app.utils.public import refresh_api_list
from app.core.config import APP_SETTINGS
from app.core.init_app import modify_db, make_middlewares
from app.log.log import LOGGING_CONFIG
from app.models import Log
from app.models.base import LogType, LogDetailType


@asynccontextmanager
async def lifespan(_app: FastAPI):
    start_time = time.time()
    try:
        await modify_db()
        await refresh_api_list()
        await Log.create(log_type=LogType.SystemLog, log_detail_type=LogDetailType.SystemStart)
        yield
    finally:
        end_time = time.time()
        runtime = end_time - start_time
        logger.info(f"App {_app.title} runtime: {runtime} seconds")  # noqa
        await Log.create(log_type=LogType.SystemLog, log_detail_type=LogDetailType.SystemStop)


app = FastAPI(
    title=APP_SETTINGS.APP_TITLE,
    description=APP_SETTINGS.APP_DESCRIPTION,
    version=APP_SETTINGS.VERSION,
    openapi_url="/openapi.json",
    middleware=make_middlewares(),
    lifespan=lifespan
)

# 注册路由
app.include_router(api_router, prefix='/api')


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/token"
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=9998, reload=True, log_config=LOGGING_CONFIG)
