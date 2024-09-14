from typing import List, Optional

from fastapi import HTTPException
from tortoise.expressions import Q

from app.models import Role, Menu
from app.schemas.roles import RoleCreate, RoleUpdate, RoleUpdateAuthrization


class RoleService:

    async def create(self, obj_in: RoleCreate) -> Role:
        role_data = obj_in.model_dump()
        role = await Role.create(**role_data)
        return role

    async def get(self, id: int) -> Optional[Role]:
        return await Role.get_or_none(id=id)

    async def list(self, page: int = 1, page_size: int = 10, search: Q = None, order: List[str] = None):
        query = Role.all()
        if search:
            query = query.filter(search)
        if order:
            query = query.order_by(*order)
        total = await query.count()
        roles = await query.offset((page - 1) * page_size).limit(page_size)
        return total, roles

    async def update(self, role_id: int, obj_in: RoleUpdate) -> Optional[Role]:
        role = await Role.get(id=role_id)
        if not role:
            return None
        role_data = obj_in.model_dump(exclude_unset=True)
        for field, value in role_data.items():
            setattr(role, field, value)
        await role.save()
        return role

    async def remove(self, id: int):
        role = await Role.get(id=id)
        await role.delete()

    async def update_menus(self, role_id: int, role_in: RoleUpdateAuthrization):
        role = await Role.get(id=role_id)
        if role_in.role_home is not None:
            role.role_home = role_in.role_home
            await role.save()
        if role_in.menu_ids:
            await role.menus.clear()
            for menu_id in role_in.menu_ids:
                menu = await Menu.get(id=menu_id)
                await role.menus.add(menu)
                while menu.parent_id != 0:
                    parent_menu = await Menu.get(id=menu.parent_id)
                    await role.menus.add(parent_menu)
                    menu = parent_menu
        return role

    async def get_role_menus(self, role_id: int):
        role = await Role.get_or_none(id=role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        if role.role_code == "R_SUPER":
            menu_objs = await Menu.filter(constant=False)
        else:
            menu_objs = await role.menus.all()
        return role.role_home, [menu_obj.id for menu_obj in menu_objs]

    async def to_dict(self, role: Role):
        return await role.to_dict()

    async def get_by_code(self, role_code: str) -> Role | None:
        return await Role.filter(role_code=role_code).first()


role_service = RoleService()
