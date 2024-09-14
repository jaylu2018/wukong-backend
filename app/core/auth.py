from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.models import User
from app.services.auth import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    token_data = auth_service.decode_token(token)
    user = await User.get_or_none(id=token_data.userId)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
