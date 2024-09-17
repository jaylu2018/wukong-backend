from typing import List, Optional, Any

from fastapi import HTTPException

from app.models import Role, Menu
from app.schemas.roles import RoleCreate, RoleUpdate, RoleUpdateAuthorization
from app.services.base import CRUDBase


class RoleService(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(Role)

    async def get_role_menus(self, role_id: int) -> tuple[Any, list[Any]]:
        role = await self.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        role_home = role.role_home
        menus = await role.menus.all()
        menu_ids = [menu.id for menu in menus]
        return role_home, menu_ids

    async def update_role_menus(self, role_id: int, menu_ids: List[int]) -> bool:
        role = await self.get(role_id)
        if not role:
            return False
        await role.menus.clear()
        for menu_id in menu_ids:
            menu = await Menu.get_or_none(id=menu_id)
            if menu:
                await role.menus.add(menu)
        return True

    async def update(self, id: int, obj_in: RoleUpdate) -> Optional[Role]:
        role = await self.get(id)
        if not role:
            return None
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"menus"})
        await role.update_from_dict(update_data).save()
        if obj_in.menus is not None:
            await self.update_role_menus(id, obj_in.menus)
        return role

    async def get_by_code(self, role_code: str) -> Role | None:
        return await Role.filter(role_code=role_code).first()


role_service = RoleService()
