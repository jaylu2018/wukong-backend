from typing import Optional
from fastapi import HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.core.log import logger, insert_log
from app.models import User
from app.core.settings import APP_SETTINGS
from app.models.base import LogType, StatusType, LogDetailType
from app.schemas.auth import TokenPayload, CredentialsSchema
from app.schemas.users import UserCreate, UserUpdate
from app.services.base import CRUDBase

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    def verify_password(self, plain_password, hashed_password):
        logger.debug(f"Verifying password. Hashed password: {hashed_password}")
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    async def authenticate_user(self, credentials: CredentialsSchema):
        user = await User.get_or_none(user_name=credentials.user_name)
        if not user:
            await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserLoginUserNameVaild)
            raise HTTPException(status_code=404, detail="用户未找到！")

        logger.debug(f"Input password: {credentials.password}")
        logger.debug(f"Stored hashed password: {user.password}")

        if not self.verify_password(credentials.password, user.password):
            await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserLoginErrorPassword)
            raise HTTPException(status_code=404, detail="用户名或密码不正确！")

        if user.status == StatusType.disable:
            await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserLoginForbid)
            raise HTTPException(status_code=404, detail="用户已被禁用！")
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=APP_SETTINGS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, APP_SETTINGS.SECRET_KEY, algorithm=APP_SETTINGS.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, APP_SETTINGS.SECRET_KEY, algorithms=[APP_SETTINGS.JWT_ALGORITHM])
            token_data = TokenPayload(**payload)
        except JWTError:
            raise HTTPException(status_code=401, detail="无效的Token")
        return token_data


auth_service = AuthService()
