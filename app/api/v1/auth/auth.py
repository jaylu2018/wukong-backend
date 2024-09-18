from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.models.base import LogType, LogDetailType
from app.services.auth import auth_service
from app.schemas.auth import Token, CredentialsSchema
from app.schemas.base import Success
from app.core.dependency import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

from app.core.log import insert_log

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await auth_service.authenticate_user(CredentialsSchema(user_name=form_data.username, password=form_data.password))
    access_token = auth_service.create_access_token(data={"userId": user.id, "userName": user.user_name, "tokenType": "accessToken"})
    await insert_log(log_type=LogType.AdminLog, log_detail_type=LogDetailType.Token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(credentials: CredentialsSchema):
    user = await auth_service.authenticate_user(credentials)
    access_token = auth_service.create_access_token(data={"userId": user.id, "userName": user.user_name, "tokenType": "accessToken"}, )
    token_data = auth_service.decode_token(access_token)
    if datetime.now(timezone.utc) > token_data.exp:  # 检查令牌是否过期
        raise HTTPException(status_code=401, detail="令牌已过期")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    # 实际上,对于JWT,我们不需要在服务器端做任何事情
    # 客户端只需要删除本地存储的token即可
    return Success(msg="Logged out successfully")


@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.user_name, "email": current_user.user_email}
