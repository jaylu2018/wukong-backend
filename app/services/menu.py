from typing import List, Optional

from app.models import Menu
from app.schemas.menus import MenuCreate, MenuUpdate, MenuOut
from app.services.base import CRUDBaseService
from app.services.role import role_service


class MenuService(CRUDBaseService[Menu, MenuCreate, MenuUpdate]):
    def __init__(self):
        super().__init__(Menu)

    async def get_menus_by_role(self, role_id: int) -> List[Menu]:
        """
        根据角色ID获取菜单列表
        :param role_id: 角色ID
        :return: 菜单列表
        """
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
        """
        递归生成菜单树
        :param menus: 菜单列表
        :param parent_id: 父菜单ID
        :return: 菜单树列表
        """
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                # 递归获取子菜单
                children = await self.build_menu_tree(menus, menu.id)
                menu_dict = await menu_service.to_dict(menu)
                if children:
                    menu_dict["children"] = children
                tree.append(menu_dict)
        return tree

    async def to_dict(self, menu: Menu) -> dict:
        return await Menu.to_dict(menu, schema=MenuOut, m2m=False)


menu_service = MenuService()
