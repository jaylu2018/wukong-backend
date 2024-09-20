from fastapi.requests import Request
from fastapi.responses import JSONResponse


async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "msg": "服务器内部错误，请联系管理员。",
            "data": None
        }
    )


async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={
            "code": 400,
            "msg": f"参数错误：{str(exc)}",
            "data": None
        }
    )
