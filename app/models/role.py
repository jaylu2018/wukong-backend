from tortoise import fields
from .base import CRUDBaseModel, StatusType


class Role(CRUDBaseModel):
    id = fields.IntField(primary_key=True, description="角色ID")
    role_name = fields.CharField(max_length=20, unique=True, description="角色名称")
    role_code = fields.CharField(max_length=20, unique=True, description="角色编码")
    role_desc = fields.CharField(max_length=500, null=True, blank=True, description="角色描述")
    role_home = fields.CharField(default="home", max_length=100, description="角色首页")
    status = fields.CharEnumField(enum_type=StatusType, default=StatusType.enable, description="状态")

    menus = fields.ManyToManyField("app_system.Menu", related_name="role_menus")
    apis = fields.ManyToManyField("app_system.Api", related_name="role_apis")

    class Meta:
        table = "roles"
