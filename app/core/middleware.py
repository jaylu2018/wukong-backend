import time
import uuid

from typing import Callable, Awaitable
from starlette.types import ASGIApp
from starlette.responses import Response
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.context_vars import trace_id_var
from app.core.log import logger
from app.core.settings import APP_SETTINGS


def register_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=APP_SETTINGS.CORS_ORIGINS,
            allow_credentials=APP_SETTINGS.CORS_ALLOW_CREDENTIALS,
            allow_methods=APP_SETTINGS.CORS_ALLOW_METHODS,
            allow_headers=APP_SETTINGS.CORS_ALLOW_HEADERS,
        ),
        Middleware(TraceIDMiddleware),
        Middleware(AccessLogMiddleware),
    ]
    return middleware


class AccessLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        # 读取并保存请求体
        request_body = await request.body()

        # 创建一个新的接收器，以防止请求体被消耗
        async def receive():
            return {'type': 'http.request', 'body': request_body}

        request = Request(request.scope, receive)

        # 捕获响应
        response = await call_next(request)

        # 读取并保存响应体
        response_body = b''
        # 由于 response.body_iterator 是异步迭代器，我们需要异步读取
        async for chunk in response.body_iterator:
            response_body += chunk

        # 重置响应的 body_iterator，以正常返回响应
        async def response_body_generator():
            yield response_body

        response.body_iterator = response_body_generator()

        process_time = (time.time() - start_time) * 1000  # 转换为毫秒

        client_ip = request.client.host
        method = request.method
        url = str(request.url)
        status_code = response.status_code
        user_agent = request.headers.get('User-Agent', 'N/A')

        # 获取 trace_id
        trace_id = request.state.trace_id if hasattr(request.state, 'trace_id') else 'N/A'

        # 自定义日志格式
        logger.bind(trace_id=trace_id).info(
            f'{client_ip} - "{method} {url}" {status_code} - {process_time:.2f}ms '
            f'Request Body: {request_body.decode("utf-8", "ignore")} \n'
            f'Response Body: {response_body.decode("utf-8", "ignore")}'
        )

        return response


class TraceIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
            self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # 生成唯一的 trace_id
        trace_id = str(uuid.uuid4())
        # 将 trace_id 存储到请求的 state 中
        request.state.trace_id = trace_id
        # 将 trace_id 设置到 ContextVar 中
        trace_id_var.set(trace_id)
        # 绑定 trace_id 到全局 logger
        logger.configure(extra={"trace_id": trace_id})
        # 继续处理请求
        response = await call_next(request)
        # 在响应头中添加 trace_id，方便客户端获取
        response.headers["X-Trace-ID"] = trace_id
        return response
