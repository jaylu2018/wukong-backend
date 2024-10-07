from typing import Annotated

from pydantic import Field, ConfigDict

from app.models.base import LogType
from app.schemas.base import CRUDBaseSchema


class BaseLog(CRUDBaseSchema):
    log_type: Annotated[LogType | None, Field(alias="logType", description="日志类型")] = None
    by_user: Annotated[str | None, Field(alias="logUser", description="操作人")] = None
    log_detail: Annotated[str | None, Field(alias="logDetail", description="日志详细")] = None

    model_config = ConfigDict(populate_by_name=True)


class BaseAPILog(CRUDBaseSchema):
    ip_address: Annotated[str | None, Field(max_length=50, description="IP地址")] = None
    user_agent: Annotated[str | None, Field(max_length=255, description="User-Agent")] = None
    request_url: Annotated[str | None, Field(max_length=255, description="请求URL")] = None
    request_params: Annotated[dict | list | None, Field(description="请求参数")] = None
    request_data: Annotated[dict | list | None, Field(description="请求数据")] = None
    response_data: Annotated[dict | list | None, Field(description="响应数据")] = None
    response_status: Annotated[bool | None, Field(description="请求状态")] = None
    process_time: Annotated[float | None, Field(description="请求处理时间")] = None

    model_config = ConfigDict(populate_by_name=True)


class LogCreate(BaseLog):
    ...


class LogUpdate(BaseLog):
    ...


__all__ = ["BaseLog", "BaseAPILog", "LogCreate", "LogUpdate"]
