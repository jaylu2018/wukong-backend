from typing import Any

import jwt
from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.core.settings import APP_SETTINGS
from app.core.context_vars import user_id_var
from app.models import User, Role
from app.models.base import StatusType
from app.services.auth import auth_service
from app.utils.tools import check_url

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(token: str = Depends(oauth2_schema)) -> User:
    token_data = auth_service.decode_token(token)
    user = await User.get_or_none(id=token_data.userId)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    user_id_var.set(user.id)
    return user


def check_token(token: str) -> tuple[bool, int, Any]:
    try:
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        decode_data = jwt.decode(token, APP_SETTINGS.SECRET_KEY, algorithms=[APP_SETTINGS.JWT_ALGORITHM], options=options)
        return True, 0, decode_data
    except jwt.DecodeError:
        return False, 4010, "无效的Token"
    except jwt.ExpiredSignatureError:
        return False, 4010, "登录已过期"
    except Exception as e:
        return False, 5000, f"{repr(e)}"


class AuthService:
    @classmethod
    async def is_authed(cls, token: str = Depends(oauth2_schema)) -> User | None:
        user_id = user_id_var.get()
        if not user_id:
            status, code, decode_data = check_token(token)
            if not status:
                raise HTTPException(status_code=code, detail=decode_data)

            if "tokenType" not in decode_data or decode_data["tokenType"] != "accessToken":
                raise HTTPException(status_code=4010, detail="The token is not an access token")

            user_id = decode_data["userId"]

        user = await User.filter(id=user_id).first()
        if not user:
            raise HTTPException(status_code=4040, detail=f"Authentication failed, the user_id: {user_id} does not exists in the system.")
        user_id_var.set(user_id)
        return user


class PermissionService:

    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthService.is_authed)) -> None:
        user_roles: list[Role] = await current_user.roles
        user_roles_codes: list[str] = [r.role_code for r in user_roles]
        if "R_SUPER" in user_roles_codes:  # 超级管理员
            return

        if not user_roles:
            raise HTTPException(status_code=4040, detail="The user is not bound to a role")

        method = request.method.lower()
        path = request.url.path

        apis = [await role.apis for role in user_roles]
        permission_apis = list(set((api.method.value, api.path, api.status) for api in sum(apis, [])))
        for (api_method, api_path, api_status) in permission_apis:
            if api_method == method and check_url(api_path, request.url.path):  # API权限检测通过
                if api_status == StatusType.disable:
                    raise HTTPException(status_code=4030, detail=f"The API has been disabled, method: {method} path: {path}")
                return

        raise HTTPException(status_code=4030, detail=f"Permission denied, method: {method} path: {path}")


DependAuth = Depends(AuthService.is_authed)
DependPermission = Depends(PermissionService.has_permission)
