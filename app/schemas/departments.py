from typing import Optional, List
from pydantic import Field, ConfigDict

from app.schemas.base import CRUDBaseSchema


class DepartmentBase(CRUDBaseSchema):
    name: str = Field(description="部门名称")
    manager_name: Optional[str] = Field(None, alias="managerName", description="负责人名称")
    manager_id: Optional[int] = Field(None, alias="managerId", description="负责人ID")
    order: int = Field(default=0, description="排序")
    parent_id: int = Field(alias="parentId", default=0, description="上级部门ID")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=True, from_attributes=True)


class DepartmentOut(DepartmentBase):
    id: Optional[int] = Field(None, alias="departmentId", description="部门ID")
    children: Optional[List['DepartmentOut']] = None


class DepartmentCreate(DepartmentBase):
    ...


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = Field(None, description="部门名称")


class DepartmentSearch(CRUDBaseSchema):
    name: str = Field(description="部门名称")
