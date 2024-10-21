from datetime import datetime
from enum import Enum
from typing import Type
from uuid import UUID
from pydantic import BaseModel
from tortoise import models, fields

from app.core.settings import APP_SETTINGS


class CRUDBaseModel(models.Model):
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True

    async def to_dict(
            self,
            schema: Type[BaseModel],
            include_fields: list[str] | None = None,
            exclude_fields: list[str] | None = None,
            m2m: bool = False
    ) -> dict:
        include_fields = set(include_fields) if include_fields else set()
        exclude_fields = set(exclude_fields) if exclude_fields else set()

        # 获取模型字段与 Pydantic 模型字段的别名映射
        field_alias_map = {}
        for field_name, model_field in schema.model_fields.items():
            alias = model_field.alias or field_name
            field_alias_map[field_name] = alias

        # 获取需要序列化的字段
        fields_to_serialize = set(self._meta.fields_map.keys())
        if m2m:
            fields_to_serialize |= set(self._meta.fetch_fields)
        if include_fields:
            fields_to_serialize &= include_fields
        if exclude_fields:
            fields_to_serialize -= exclude_fields

        result = {}
        for field_name in fields_to_serialize:
            value = getattr(self, field_name, None)

            # 获取字段对应的别名，如果获取不到，则使用原始字段名
            alias = field_alias_map.get(field_name, field_name)

            # 处理关系字段
            field_object = self._meta.fields_map.get(field_name)
            if isinstance(field_object, fields.relational.RelationalField):
                if m2m and isinstance(field_object, fields.relational.ManyToManyFieldInstance):
                    related_objects = await value.all()
                    related_schema = schema.model_fields[field_name].annotation.__args__[0]
                    if isinstance(related_schema, type) and issubclass(related_schema, BaseModel):
                        result[alias] = [await obj.to_dict(schema=related_schema) for obj in related_objects]
                    else:
                        # 如果related_schema是基本类型，例如str
                        result[alias] = [obj for obj in related_objects]
                elif isinstance(field_object, fields.relational.ForeignKeyFieldInstance):
                    related_obj = await value
                    if related_obj:
                        related_schema = schema.model_fields[field_name].annotation
                        result[alias] = await related_obj.to_dict(schema=related_schema)
                    else:
                        result[alias] = None
                else:
                    continue
            else:
                # 处理基本数据类型
                if isinstance(value, datetime):
                    value = value.strftime(APP_SETTINGS.DATETIME_FORMAT)
                elif isinstance(value, UUID):
                    value = str(value)
                elif isinstance(value, Enum):
                    value = value.value
                result[alias] = value

        return result


class EnumBase(Enum):
    @classmethod
    def get_member_values(cls):
        return [item.value for item in cls._member_map_.values()]

    @classmethod
    def get_member_names(cls):
        return [name for name in cls._member_names_]


class IntEnum(int, EnumBase):
    ...


class StrEnum(str, EnumBase):
    ...


class MethodType(str, Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


class LogType(str, Enum):
    ApiLog = "1"
    UserLog = "2"
    AdminLog = "3"
    SystemLog = "4"


class LogDetailType(str, Enum):
    """
    1000-1999 内置
    1100-1199 系统
    1200-1299 用户
    1300-1399 部门
    1400-1499 菜单
    1500-1599 角色
    1600-1699 用户
    1700-1799 日志
    1800-1899 路由
    1900-1999 API
    """
    Default = "0000"

    Token = "1001"
    TokenRefresh = "1002"
    Login = "1003"
    Logout = "1004"
    AboutMe = "1005"
    GetUserInfo = "1006"

    SystemStart = "1101"
    SystemStop = "1102"

    UserLoginSuccess = "1201"
    UserAuthRefreshTokenSuccess = "1202"
    UserLoginGetUserInfo = "1203"
    UserLoginUserNameVaild = "1211"
    UserLoginErrorPassword = "1212"
    UserLoginForbid = "1213"

    DepartmentGetList = "1301"

    DepartmentGetOne = "1311"
    DepartmentCreateOne = "1312"
    DepartmentUpdateOne = "1313"
    DepartmentDeleteOne = "1314"
    DepartmentBatchDeleteOne = "1315"
    DepartmentGetTree = "1316"

    MenuGetList = "1401"
    MenuGetTree = "1402"
    MenuGetPages = "1403"
    MenuGetButtonsTree = "1404"

    MenuGetOne = "1411"
    MenuCreateOne = "1412"
    MenuUpdateOne = "1413"
    MenuDeleteOne = "1414"
    MenuBatchDeleteOne = "1415"

    RoleGetList = "1501"
    RoleGetMenus = "1502"
    RoleUpdateMenus = "1503"
    RoleGetButtons = "1504"
    RoleUpdateButtons = "1505"
    RoleGetApis = "1506"
    RoleUpdateApis = "1507"

    RoleGetOne = "1511"
    RoleCreateOne = "1512"
    RoleUpdateOne = "1513"
    RoleDeleteOne = "1514"
    RoleBatchDelete = "1515"

    UserGetList = "1601"
    UserGetOne = "1611"
    UserCreateOne = "1612"
    UserUpdateOne = "1613"
    UserDeleteOne = "1614"
    UserBatchDelete = "1615"

    LogGetList = "1701"
    LogGetOne = "1711"
    LogUpdate = "1712"
    LogDelete = "1713"
    LogBatchDelete = "1714"

    RouteGetList = "1801"
    RouteExists = "1802"
    RouteGetUserRoutes = "1803"
    RouteGetConstantRoutes = "1804"
    RouteGetOne = "1810"
    RouteCreateOne = "1811"
    RouteUpdateOne = "1812"
    RouteDeleteOne = "1813"
    RouteBatchDelete = "1814"

    ApiGetList = "1901"
    ApiGetTree = "1902"
    ApiRefresh = "1903"

    ApiGetOne = "1311"
    ApiCreateOne = "1312"
    ApiUpdateOne = "1313"
    ApiDeleteOne = "1314"
    ApiBatchDelete = "1315"


class StatusType(str, Enum):
    enable = "1"
    disable = "2"


class GenderType(str, Enum):
    male = "1"
    female = "2"


class MenuType(str, Enum):
    catalog = "1"  # 目录
    menu = "2"  # 菜单
    button = "3"


class IconType(str, Enum):
    iconify = "1"
    local = "2"


__all__ = ["CRUDBaseModel", "EnumBase", "IntEnum", "StrEnum", "MethodType", "LogType", "LogDetailType", "StatusType", "GenderType", "MenuType", "IconType"]
