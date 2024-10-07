from tortoise import fields
from .base import CRUDBaseModel, LogType, LogDetailType


class Log(CRUDBaseModel):
    id = fields.IntField(primary_key=True, description="日志ID")
    trace_id = fields.CharField(max_length=36, null=True, description="Trace ID")
    log_type = fields.CharEnumField(enum_type=LogType, description="日志类型")
    by_user = fields.ForeignKeyField("app_system.User", null=True, on_delete=fields.SET_NULL, description="操作人")
    api_log = fields.ForeignKeyField("app_system.APILog", null=True, on_delete=fields.SET_NULL, description="API日志")
    log_detail_type = fields.CharEnumField(enum_type=LogDetailType, null=True, description="日志详情类型")
    detail = fields.TextField(null=True, description="详细信息")
    stack_trace = fields.TextField(null=True, description="堆栈信息")

    class Meta:
        table = "logs"


class APILog(CRUDBaseModel):
    id = fields.IntField(primary_key=True, description="API日志ID")
    ip_address = fields.CharField(max_length=60, description="IP地址")
    user_agent = fields.CharField(max_length=800, description="User-Agent")
    request_url = fields.CharField(max_length=255, description="请求URL")
    request_params = fields.JSONField(null=True, description="请求参数")
    request_data = fields.JSONField(null=True, description="请求数据")
    response_data = fields.JSONField(null=True, description="响应数据")
    response_code = fields.CharField(max_length=6, null=True, description="响应业务码")
    process_time = fields.FloatField(null=True, description="请求处理时间")

    class Meta:
        table = "api_logs"
