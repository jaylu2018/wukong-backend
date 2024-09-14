from typing import Annotated, Optional, List
from pydantic import BaseModel, Field

from app.models.base import StatusType


class BaseApi(BaseModel):
    path: str = Field(..., title="请求路径", description="/api/v1/auth/login")
    method: str = Field(..., title="请求方法", description="GET")
    summary: Optional[str] = Field(None, title="API 简介")
    tags: Optional[List[str]] = Field(None, title="API 标签")
    status: Optional[StatusType] = Field(default=StatusType.enable, title="状态")

    class Config:
        allow_extra = True
        populate_by_name = True


class ApiSearch(BaseApi):
    current: Annotated[int | None, Field(title="页码")] = 1
    size: Annotated[int | None, Field(title="每页数量")] = 10


class ApiCreate(BaseApi):
    pass


class ApiUpdate(BaseModel):
    summary: Optional[str] = Field(None, title="API 简介")
    tags: Optional[List[str]] = Field(None, title="API 标签")
    status: Optional[StatusType] = Field(None, title="状态")


class ApiOut(BaseApi):
    id: int = Field(..., title="API ID")
