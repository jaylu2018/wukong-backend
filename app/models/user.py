from tortoise import fields
from .base import CRUDBaseModel, GenderType, StatusType


class User(CRUDBaseModel):
    id = fields.IntField(primary_key=True, description="用户ID")
    user_name = fields.CharField(max_length=20, unique=True, description="用户名称")
    password = fields.CharField(max_length=128, description="密码")
    nick_name = fields.CharField(max_length=30, null=True, description="昵称")
    user_gender = fields.CharEnumField(GenderType, default=GenderType.male, description="性别")
    user_email = fields.CharField(max_length=255, unique=True, description="邮箱")
    user_phone = fields.CharField(max_length=20, null=True, description="电话")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    roles = fields.ManyToManyField("app_system.Role", related_name="user_roles")
    status = fields.CharEnumField(StatusType, default=StatusType.enable, description="状态")
    department = fields.ManyToManyField('app_system.Department', related_name='users', null=True, description="所属部门")

    class Meta:
        table = "users"
