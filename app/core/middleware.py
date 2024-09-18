import uuid

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.context_vars import trace_id_var

from app.core.config import APP_SETTINGS


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=APP_SETTINGS.CORS_ORIGINS,
            allow_credentials=APP_SETTINGS.CORS_ALLOW_CREDENTIALS,
            allow_methods=APP_SETTINGS.CORS_ALLOW_METHODS,
            allow_headers=APP_SETTINGS.CORS_ALLOW_HEADERS,
        ),
    ]
    return middleware


class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 生成唯一的 trace_id
        trace_id = str(uuid.uuid4())
        # 将 trace_id 存储到请求的 state 中
        request.state.trace_id = trace_id
        # 将 trace_id 设置到 ContextVar 中
        trace_id_var.set(trace_id)
        # 继续处理请求
        response = await call_next(request)
        # 在响应头中添加 trace_id，方便客户端获取
        response.headers["X-Trace-ID"] = trace_id
        return response
