from pydantic import BaseModel
from typing import Optional

from app.models.base import MenuType, IconType, StatusType


class RouteBase(BaseModel):
    parent_id: int
    menu_type: MenuType
    menu_name: str
    route_name: str
    route_path: str
    component: str
    order: int
    i18n_key: str
    icon: str
    icon_type: IconType
    status: StatusType = StatusType.enable
    keep_alive: bool = False
    hide_in_menu: bool = False
    constant: bool = False
    redirect: Optional[str] = None
    href: Optional[str] = None
    active_menu: Optional[str] = None
    multi_tab: bool = True
    fixed_index_in_tab: Optional[int] = None


class RouteCreate(RouteBase):
    pass


class RouteUpdate(RouteBase):
    parent_id: Optional[int] = None
    menu_type: Optional[MenuType] = None
    menu_name: Optional[str] = None
    route_name: Optional[str] = None
    route_path: Optional[str] = None
    component: Optional[str] = None
    order: Optional[int] = None
    i18n_key: Optional[str] = None
    icon: Optional[str] = None
    icon_type: Optional[IconType] = None
