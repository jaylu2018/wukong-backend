from tortoise import fields
from .base import CRUDBaseModel


class Department(CRUDBaseModel):
    id = fields.IntField(primary_key=True, description="部门ID")
    name = fields.CharField(max_length=100, description="部门名称")
    manager_name = fields.CharField(max_length=50, null=True, description="负责人名称")
    manager_id = fields.IntField(null=True, description="负责人ID")
    order = fields.IntField(default=0, description="排序")
    parent_id = fields.IntField(default=0, description="上级部门ID")

    class Meta:
        table = "departments"
