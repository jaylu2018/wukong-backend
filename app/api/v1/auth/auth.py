from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.base import BaseCRUDRouter
from app.core.context_vars import user_id_var
from app.core.log import insert_log
from app.models import User
from app.schemas.auth import CredentialsSchema
from app.schemas.base import Response
from app.services.auth import auth_service
from app.core.dependency import get_current_user, DependAuth
from app.models.base import LogType, LogDetailType
from app.services.user import user_service


class AuthCRUDRouter(BaseCRUDRouter):
    def _add_routes(self):
        @self.router.post("/login", summary="用户登录")
        async def login(credentials: CredentialsSchema):
            user = await auth_service.authenticate_user(credentials)
            access_token = auth_service.create_access_token(
                data={"userId": user.id, "userName": user.user_name, "tokenType": "accessToken"}
            )
            # 插入日志
            await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["login"])
            # 返回响应
            return Response(data={"accessToken": access_token, "token_type": "bearer"})

        @self.router.post("/logout", summary="用户登出")
        async def logout():
            await insert_log(log_type=self.log_type, log_detail_type=self.log_detail_types["logout"])
            return Response(msg="Logged out successfully")

        @self.router.get("/me", summary="获取当前用户信息", dependencies=[DependAuth])
        async def read_users_me():
            current_user = await user_service.get(user_id_var.get())
            return {"username": current_user.user_name, "email": current_user.user_email}

        @self.router.get("/getUserInfo", summary="获取用户详细信息", dependencies=[DependAuth])
        async def get_user_info():
            current_user = await user_service.get(user_id_var.get())
            if not current_user:
                raise HTTPException(status_code=404, detail="用户不存在")
            # 获取用户基本信息
            user_dict = current_user.__dict__

            # 获取用户角色列表
            roles = [{"code": role.role_code, "id": role.id} for role in await current_user.roles.all()]

            # 获取用户按钮权限
            buttons = set()
            for role in await current_user.roles.all():
                role_buttons = await role.buttons.all()
                buttons.update([button.button_code for button in role_buttons])
            buttons = list(buttons)

            # 构建返回的数据字典
            data = {
                "nickName": user_dict.get("nick_name"),
                "id": current_user.id,
                "updateTime": user_dict.get("update_time").strftime("%Y-%m-%d %H:%M:%S") if user_dict.get("update_time") else None,
                "userName": current_user.user_name,
                "lastLogin": user_dict.get("last_login").strftime("%Y-%m-%d %H:%M:%S") if user_dict.get("last_login") else None,
                "userPhone": current_user.user_phone,
                "createTime": user_dict.get("create_time").strftime("%Y-%m-%d %H:%M:%S") if user_dict.get("create_time") else None,
                "status": current_user.status.value,
                "userGender": current_user.user_gender.value,
                "userEmail": current_user.user_email,
                "user_id": current_user.id,
                "roles": roles,
                "buttons": buttons
            }
            return Response(data=data)

    # 定义日志详细类型


log_detail_types = {
    "login": LogDetailType.Login,
    "logout": LogDetailType.Logout,
    "get_user_info": LogDetailType.GetUserInfo,
}

# 创建路由器实例
router = APIRouter()
auth_router = AuthCRUDRouter(
    model=User,
    create_schema=CredentialsSchema,
    update_schema=CredentialsSchema,
    service=auth_service,
    log_detail_types=log_detail_types,
    get_current_user=get_current_user,
    prefix="",
    tags=["权限认证"],
    log_type=LogType.AdminLog,
)


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.authenticate_user(CredentialsSchema(user_name=form_data.username, password=form_data.password))
    access_token = auth_service.create_access_token(data={"userId": user.id, "userName": user.user_name, "tokenType": "accessToken"})
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.Token)
    return {"access_token": access_token, "token_type": "bearer"}


router.include_router(auth_router.router)
