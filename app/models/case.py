# from tortoise import fields
# from app.models.base import BaseModel, TimestampMixin, StatusType
#
#
# class Case(BaseModel, TimestampMixin):
#     id = fields.IntField(primary_key=True, description="案例ID")
#     case_name = fields.CharField(max_length=255, description="案例名称")
#     description = fields.TextField(null=True, description="案例描述")
#     status = fields.CharEnumField(enum_type=StatusType, default=StatusType.enable, description="状态")
#     created_by = fields.ForeignKeyField("models.User", related_name="created_cases", on_delete=fields.CASCADE, description="创建人")
#     priority = fields.IntField(default=0, description="优先级")
#
#     class Meta:
#         table = "cases"
