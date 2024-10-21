from typing import List, Optional
from pydantic import EmailStr, Field, BaseModel, ConfigDict

from app.models.base import GenderType, StatusType
from app.schemas.base import CRUDBaseSchema


class UserBase(BaseModel):
    user_name: str = Field(..., alias="userName", max_length=20)
    user_email: EmailStr = Field(..., alias="userEmail")
    user_gender: GenderType = Field(GenderType.male, alias="userGender")
    nick_name: Optional[str] = Field(None, alias="nickName", max_length=30)
    user_phone: Optional[str] = Field(None, alias="userPhone", max_length=20)
    roles: Optional[List[str]] = Field(default_factory=list, alias="userRoles")
    status: StatusType = Field(StatusType.enable)
    department_id: Optional[int] = Field(None, alias="departmentId")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(CRUDBaseSchema):
    user_email: Optional[EmailStr] = Field(None, alias="userEmail")
    user_gender: Optional[GenderType] = Field(None, alias="userGender")
    nick_name: Optional[str] = Field(None, alias="nickName", max_length=30)
    user_phone: Optional[str] = Field(None, alias="userPhone", max_length=20)
    roles: Optional[List[str]] = Field(None, alias="userRoles")
    status: StatusType = Field(StatusType.enable,alias="status")
    password: Optional[str] = Field(None, min_length=6, max_length=128)

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)


class UserOut(CRUDBaseSchema):
    id: int = Field(..., alias="employeeId")
    user_name: str = Field(..., alias="userName")
    user_email: EmailStr = Field(..., alias="userEmail")
    user_gender: GenderType = Field(..., alias="userGender")
    nick_name: Optional[str] = Field(None, alias="nickName")
    user_phone: Optional[str] = Field(None, alias="userPhone")
    roles: List[str] = Field(..., alias="userRoles")
    status: StatusType = Field(StatusType.enable,alias="status")
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, from_attributes=True)
