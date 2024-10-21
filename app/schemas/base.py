from datetime import datetime
from typing import Generic, TypeVar, Optional, Annotated

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class CRUDBaseSchema(BaseModel):
    create_time: Annotated[datetime | None, Field(alias="createTime", description="创建时间")] = None
    update_time: Annotated[datetime | None, Field(alias="updateTime", description="更新时间")] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Response(BaseModel, Generic[T]):
    code: int = Field(default=0)
    msg: str = Field(default="OK")
    data: Optional[T] = None


class DataList(BaseModel, Generic[T]):
    records: T
    total: Optional[int] = None
    current: Optional[int] = None
    size: Optional[int] = None


class ResponseList(BaseModel, Generic[T]):
    code: int = Field(default=0)
    msg: str = Field(default="OK")
    data: DataList[T]

    model_config = ConfigDict(from_attributes=True)
