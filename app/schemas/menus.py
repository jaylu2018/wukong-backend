from typing import Optional

from pydantic import Field, ConfigDict

from app.models.base import MenuType
from app.schemas.base import CRUDBaseSchema


class MenuBase(CRUDBaseSchema):
    menu_name: str = Field(alias="menuName", description="菜单名称")
    menu_type: MenuType = Field(alias="menuType", description="菜单类型")
    route_path: Optional[str] = Field(None, alias="path", description="路由路径")
    sort: int = Field(description="菜单顺序")
    component: Optional[str] = Field(None, description="路由组件")
    parent_id: int = Field(0, alias="parentId", description="父菜单ID")
    icon: Optional[str] = Field(None, description="图标名称")
    keep_alive: Optional[bool] = Field(None, description="是否缓存")
    visible_flag: Optional[bool] = Field(alias="visibleFlag", description="是否可见")
    status: str = Field(description="状态")
    web_permission: Optional[str] = Field(alias="webPerms", description="前端权限")
    api_permission: Optional[str] = Field(alias="apiPerms", description="后段权限")

    model_config = ConfigDict(populate_by_name=True)


class MenuCreate(MenuBase):
    ...


class MenuUpdate(MenuCreate):
    ...


class MenuOut(MenuBase):
    id: int = Field(alias="menuId", description="菜单ID")
    href: Optional[str] = Field(None, description="外链")


class MenuSearch(CRUDBaseSchema):
    menu_name: str = Field(alias="menuName", description="菜单名称")
