from tortoise import fields
from .base import BaseModel, TimestampMixin, StatusType


class Button(BaseModel, TimestampMixin):
    id = fields.IntField(pk=True, description="菜单ID")
    button_code = fields.CharField(max_length=200, description="按钮编码")
    button_desc = fields.CharField(max_length=200, description="按钮描述")
    status = fields.CharEnumField(enum_type=StatusType, default=StatusType.enable, description="状态")

    class Meta:
        table = "buttons"
