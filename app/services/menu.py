from typing import List, Optional

from app.models import Menu, Button
from app.schemas.menus import MenuCreate, MenuUpdate
from app.services.base import CRUDBase


class MenuService(CRUDBase[Menu, MenuCreate, MenuUpdate]):
    def __init__(self):
        super().__init__(Menu)

    async def get_non_constant_menus(self) -> List[Menu]:
        return await self.model.filter(constant=False)

    async def update(self, id: int, menu_in: MenuUpdate) -> Optional[Menu]:
        menu = await self.get(id)
        if not menu:
            return None

        update_data = menu_in.model_dump(exclude_unset=True, exclude={"buttons"})
        await menu.update_from_dict(update_data).save()

        if menu_in.buttons is not None:
            await menu.buttons.clear()
            for button_id in menu_in.buttons:
                button = await Button.get_or_none(id=button_id)
                if button:
                    await menu.buttons.add(button)

        return menu

    async def get_first_level_menus(self) -> List[Menu]:
        return await self.model.filter(parent_id=0)

    async def get_menus_with_buttons(self) -> List[Menu]:
        return await self.model.filter(buttons__isnull=False).distinct()

    async def add_button(self, menu_id: int, button_id: int) -> bool:
        menu = await self.get(menu_id)
        button = await Button.get_or_none(id=button_id)
        if not menu or not button:
            return False
        await menu.buttons.add(button)
        return True

    async def get_menus_with_buttons(self) -> List[Menu]:
        return await Menu.filter(buttons__menu_buttons__not=None).distinct()


menu_service = MenuService()
