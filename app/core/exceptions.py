from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误，请联系管理员。",
            "data": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    for err in errors:
        field_errors = err.get('loc', [])
        field_path = [str(loc) for loc in field_errors if isinstance(loc, (str, int))]
        # 跳过第一个 "body"
        if field_path and field_path[0] == 'body':
            field_name = '.'.join(field_path[1:])
        else:
            field_name = '.'.join(field_path)
        message = f"{field_name} 字段格式校验失败"
        error_messages.append(message)
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"code": "422", "msg": "参数验证错误", "data": error_messages},
    )
