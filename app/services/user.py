from typing import List
from fastapi import HTTPException

from app.models import Role, User
from app.schemas.users import UserCreate, UserUpdate, UserOut
from app.services.auth import auth_service
from app.services.base import CRUDBaseService


class UserService(CRUDBaseService[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def create(self, user_in: UserCreate) -> User:
        # 检查用户名是否已存在
        existing_user = await User.filter(user_name=user_in.user_name).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = await User.filter(user_email=user_in.user_email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被使用")

        # 检查角色编码是否存在
        if user_in.roles:
            roles = await Role.filter(role_code__in=user_in.roles)
            if len(roles) != len(user_in.roles):
                raise HTTPException(status_code=400, detail="一个或多个角色不存在")
        hashed_password = auth_service.get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"roles"})
        user_data["password"] = hashed_password
        user = await User.create(**user_data)
        await self.update_user_roles(user, user_in.roles)
        return user

    async def update(self, id: int, obj_in: UserUpdate) -> User:
        user = await self.get(id)
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"roles"})
        if "password" in update_data and update_data["password"]:
            update_data["password"] = auth_service.get_password_hash(update_data["password"])
        await user.update_from_dict(update_data)
        await user.save()
        if obj_in.roles is not None:
            await self.update_user_roles(user, obj_in.roles)
        return user

    @staticmethod
    async def update_user_roles(user: User, role_codes: List[str]) -> None:
        await user.roles.clear()
        roles = await Role.filter(role_code__in=role_codes)
        await user.roles.add(*roles)

    async def to_dict_with_roles(self, user: User) -> dict:
        user_dict = await self.to_dict(user)
        roles = await user.roles.all()
        user_dict["userRoles"] = [role.role_code for role in roles]
        return user_dict

    async def to_dict(self, user: User) -> dict:
        return await User.to_dict(user, schema=UserOut, m2m=False)


user_service = UserService()
