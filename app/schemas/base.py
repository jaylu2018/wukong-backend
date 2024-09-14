from typing import Any, Generic, TypeVar, Optional

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

T = TypeVar('T')


class Custom(JSONResponse):
    def __init__(
            self,
            code: str | int = "0000",
            status_code: int = 200,
            msg: str = "OK",
            data: Any = None,
            **kwargs,
    ):
        content = {"code": str(code), "msg": msg, "data": data}
        content.update(kwargs)
        super().__init__(content=content, status_code=status_code)


class Success(BaseModel, Generic[T]):
    code: str = Field(default="2000")
    msg: str = Field(default="Success")
    data: Optional[T] = None


class Fail(Custom):
    def __init__(
            self,
            code: str | int = "4000",
            msg: str = "OK",
            data: Any = None,
            **kwargs,
    ):
        super().__init__(code=code, msg=msg, data=data, status_code=200, **kwargs)


class SuccessExtra(BaseModel, Generic[T]):
    code: str = Field(default="2000")
    msg: str = Field(default="Success")
    data: Optional[T] = None
    total: Optional[int] = None
    current: Optional[int] = None
    size: Optional[int] = None
