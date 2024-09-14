from typing import Optional

from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.core.exceptions import HTTPException
from app.log import logger
from app.models import User, Log
from app.core.config import APP_SETTINGS
from app.models.base import LogType, StatusType, LogDetailType
from app.schemas.auth import TokenPayload, CredentialsSchema

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
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
            await Log.create(log_type=LogType.UserLog, by_user_id=0, log_detail_type=LogDetailType.UserLoginUserNameVaild)
            raise HTTPException(code="4040", msg="用户未找到！")

        logger.debug(f"Input password: {credentials.password}")
        logger.debug(f"Stored hashed password: {user.password}")

        if not self.verify_password(credentials.password, user.password):
            await Log.create(log_type=LogType.UserLog, by_user_id=user.id, log_detail_type=LogDetailType.UserLoginErrorPassword)
            raise HTTPException(code="4041", msg="用户名或密码不正确！")

        if user.status == StatusType.disable:
            await Log.create(log_type=LogType.UserLog, by_user_id=user.id, log_detail_type=LogDetailType.UserLoginForbid)
            raise HTTPException(code="4042", msg="用户已被禁用！")
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
            raise HTTPException(code="4010", msg="Could not validate credentials")
        return token_data


auth_service = AuthService()
