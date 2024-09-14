from fastapi.routing import APIRoute
from loguru import logger

from app.core.ctx import CTX_USER_ID
from app.models import Api, Log
from app.models.base import LogType, LogDetailType


async def refresh_api_list():
    from app.main import app
    api_list = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            path = route.path
            method = route.methods.pop().lower() if route.methods else "get"
            summary = route.summary or ""
            tags = route.tags or []
            api_list.append((path, method, summary, tags))

    existing_apis = await Api.all()
    existing_api_set = {(api.path, api.method) for api in existing_apis}

    for path, method, summary, tags in api_list:
        if (path, method) not in existing_api_set:
            await Api.create(path=path, method=method, summary=summary, tags=tags)
        else:
            await Api.filter(path=path, method=method).update(summary=summary, tags=tags)

    new_api_set = set((path, method) for path, method, _, _ in api_list)
    for api in existing_apis:
        if (api.path, api.method) not in new_api_set:
            await api.delete()

    logger.info(f"API列表刷新完成，共{len(api_list)}个API")


async def insert_log(log_type: LogType, log_detail_type: LogDetailType, by_user_id: int | None = None):
    """
    插入日志
    :param log_type:
    :param log_detail_type:
    :param by_user_id: 0为从上下文获取当前用户id, 需要请求携带token
    :return:
    """
    if by_user_id == 0 and (by_user_id := CTX_USER_ID.get()) == 0:
        by_user_id = None

    await Log.create(log_type=log_type, log_detail_type=log_detail_type, by_user_id=by_user_id)
