from fastapi.routing import APIRoute

from app.core.log import logger
from app.models import Api


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
