from typing import List, Optional

from app.models import Menu
from app.schemas.menus import MenuCreate, MenuUpdate, MenuOut
from app.services.base import CRUDBaseService
from app.services.role import role_service


class MenuService(CRUDBaseService[Menu, MenuCreate, MenuUpdate]):
    def __init__(self):
        super().__init__(Menu)

    @staticmethod
    async def get_menus_by_role(role_id: int) -> List[Menu]:
        role = await role_service.get(role_id)
        if not role:
            return []
        return await role.menus

    async def update(self, id: int, obj_in: MenuUpdate) -> Optional[Menu]:
        menu = await self.get(id)
        if not menu:
            return None
        update_data = obj_in.model_dump(exclude_unset=True)
        await menu.update_from_dict(update_data).save()
        return menu

    async def build_menu_tree(self, menus: List[Menu], parent_id: int = 0) -> List[dict]:
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = await self.build_menu_tree(menus, menu.id)  # 递归获取子菜单
                menu_dict = await menu_service.to_dict(menu)
                if children:
                    menu_dict["children"] = children
                tree.append(menu_dict)
        return tree

    async def to_dict(self, menu: Menu) -> dict:
        return await Menu.to_dict(menu, schema=MenuOut, m2m=False)


menu_service = MenuService()
