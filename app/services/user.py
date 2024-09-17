from typing import List, Optional

from app.models import Role, User
from app.schemas.users import UserCreate, UserUpdate
from app.services.auth import auth_service
from app.services.base import CRUDBase


class UserService(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def create(self, user_in: UserCreate) -> User:
        hashed_password = auth_service.get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"roles"})
        user_data["password"] = hashed_password
        user = await User.create(**user_data)
        if user_in.roles:
            await self.update_user_roles(user, user_in.roles)
        return user

    async def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        user = await self.get(user_id)
        if not user:
            return None
        update_data = user_in.model_dump(exclude_unset=True, exclude={"roles"})
        if "password" in update_data and update_data["password"]:
            update_data["password"] = auth_service.get_password_hash(update_data["password"])
        await user.update_from_dict(update_data)
        await user.save()
        if user_in.roles is not None:
            await self.update_user_roles(user, user_in.roles)
        return user

    @staticmethod
    async def update_user_roles(user: User, role_codes: List[str]) -> None:
        await user.roles.clear()
        roles = await Role.filter(role_code__in=role_codes)
        await user.roles.add(*roles)

    async def to_dict_with_roles(self, user: User) -> dict:
        user_dict = await super().to_dict(user)
        roles = await user.roles.all()
        user_dict["roles"] = [role.role_code for role in roles]
        return user_dict


user_service = UserService()
