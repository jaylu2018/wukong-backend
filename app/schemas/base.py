from datetime import datetime
from typing import Generic, TypeVar, Optional, Annotated

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class BaseSchema(BaseModel):
    create_time: Annotated[datetime | None, Field(alias="creationTime", description="创建时间")] = None
    update_time: Annotated[datetime | None, Field(alias="updateTime", description="更新时间")] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class Success(BaseModel, Generic[T]):
    code: str = Field(default="2000")
    msg: str = Field(default="Success")
    data: Optional[T] = None


class SuccessExtra(BaseModel, Generic[T]):
    code: str = Field(default="2000")
    msg: str = Field(default="Success")
    data: Optional[T] = None
    total: Optional[int] = None
    current: Optional[int] = None
    size: Optional[int] = None
