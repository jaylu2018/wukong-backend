from tortoise import fields
from .base import CRUDBaseModel, MenuType, StatusType


class Menu(CRUDBaseModel):
    id = fields.IntField(primary_key=True, description="菜单ID")
    menu_name = fields.CharField(max_length=100, description="菜单名称")
    menu_type = fields.CharEnumField(enum_type=MenuType, description="菜单类型")
    route_path = fields.CharField(null=True,max_length=200, description="路由路径")
    sort = fields.IntField(default=0, description="菜单顺序")
    component = fields.CharField(null=True, max_length=100, description="路由组件")
    parent_id = fields.IntField(default=0, max_length=10, description="父菜单ID")
    icon = fields.CharField(null=True, max_length=100, description="图标名称")
    href = fields.CharField(null=True, max_length=200, description="外链")
    keep_alive = fields.BooleanField(default=False, description="是否缓存")
    visible_flag = fields.BooleanField(default=False, description="是否可见")
    status = fields.CharEnumField(enum_type=StatusType, default=StatusType.enable, description="状态")
    web_permission = fields.CharField(null=True, max_length=200, description="前端权限")
    api_permission = fields.CharField(null=True, max_length=200, description="后段权限")


    class Meta:
        table = "menus"
