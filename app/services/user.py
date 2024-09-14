from typing import List, Optional
from tortoise.expressions import Q

from app.models import User, Role
from app.schemas.users import UserCreate, UserUpdate
from app.services.auth import auth_service


class UserService:
    async def create(self, obj_in: UserCreate) -> User:
        obj_in.password = auth_service.get_password_hash(password=obj_in.password)
        user_data = obj_in.model_dump(exclude={"roles"})
        user = await User.create(**user_data)
        return user

    async def update(self, user_id: int, obj_in: UserUpdate) -> Optional[User]:
        user = await User.get(id=user_id)
        if not user:
            return None
        user_data = obj_in.dict(exclude_unset=True)
        for field, value in user_data.items():
            setattr(user, field, value)
        await user.save()
        return user

    async def get(self, id: int) -> Optional[User]:
        return await User.get_or_none(id=id)

    async def list(self, page: int = 1, page_size: int = 10, search: Q = None, order: List[str] = None):
        query = User.all()
        if search:
            query = query.filter(search)
        if order:
            query = query.order_by(*order)
        total = await query.count()
        users = await query.offset((page - 1) * page_size).limit(page_size)
        return total, users

    async def remove(self, id: int):
        user = await User.get(id=id)
        await user.delete()

    async def exists(self):
        return await User.exists()

    async def update_roles_by_code(self, user: User, role_codes: List[str]):
        await user.roles.clear()
        for role_code in role_codes:
            role = await Role.get_or_none(role_code=role_code)
            if role:
                await user.roles.add(role)

    async def get_user_roles(self, user_id: int) -> List[Role]:
        user = await User.get(id=user_id).prefetch_related("roles")
        return user.roles

    async def to_dict(self, user: User, exclude_fields: List[str] = None):
        return await user.to_dict(exclude_fields=exclude_fields)

    async def to_dict_with_roles(self, user: User) -> dict:
        user_dict = await user.to_dict(exclude_fields=["password"])
        user_roles = await user.roles.all()
        user_dict["roles"] = [role.role_code for role in user_roles]
        return user_dict


user_service = UserService()
