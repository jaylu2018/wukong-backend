from typing import Any, Dict, List, Optional

from app.models import Role, User
from app.schemas.users import UserCreate, UserUpdate
from app.services.auth import auth_service


class UserService:
    async def create_user(self, user_in: UserCreate) -> User:
        hashed_password = auth_service.get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"roles"})
        user_data["password"] = hashed_password
        user = await User.create(**user_data)
        if user_in.roles:
            await self.update_user_roles(user, user_in.roles)
        return user

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        return await User.get_or_none(id=user_id).prefetch_related("roles")

    @staticmethod
    async def list_users(page: int = 1, page_size: int = 10, filters: Dict[str, Any] = None) -> tuple[int, List[User]]:
        query = User.all()
        if filters:
            query = query.filter(**filters)
        total = await query.count()
        users = await query.offset((page - 1) * page_size).limit(page_size)
        return total, users

    async def update_user(self, user_id: int, user_in: UserUpdate) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
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

    async def delete_user(self, user_id: int) -> bool:
        user = await self.get_user_by_id(user_id)
        if user:
            await user.delete()
            return True
        return False

    async def batch_delete_users(self, user_ids: List[int]) -> List[int]:
        deleted_ids = []
        for user_id in user_ids:
            if await self.delete_user(user_id):
                deleted_ids.append(user_id)
        return deleted_ids

    @staticmethod
    async def update_user_roles(user: User, role_codes: List[str]) -> None:
        await user.roles.clear()
        roles = await Role.filter(role_code__in=role_codes)
        await user.roles.add(*roles)

    @staticmethod
    async def to_dict_with_roles(user: User) -> dict:
        user_dict = await user.to_dict(exclude_fields=["password"])
        roles = await user.roles.all()
        user_dict["roles"] = [role.role_code for role in roles]
        return user_dict


user_service = UserService()
