from typing import List, Optional
from fastapi import HTTPException

from app.models import Menu, Button
from app.schemas.menus import MenuCreate, MenuUpdate


class MenuService:
    async def list(self, page: int = 1, page_size: int = 10, order: List[str] = None) -> tuple[int, List[Menu]]:
        query = Menu.all()
        if order:
            query = query.order_by(*order)
        total = await query.count()
        menus = await query.offset((page - 1) * page_size).limit(page_size)
        return total, menus

    async def get(self, id: int) -> Optional[Menu]:
        return await Menu.get_or_none(id=id)

    async def get_non_constant_menus(self) -> List[Menu]:
        return await Menu.filter(constant=False)

    async def create(self, menu_in: MenuCreate) -> Menu:
        menu_data = menu_in.model_dump()
        menu = await Menu.create(**menu_data)
        return menu

    async def update(self, id: int, menu_in: MenuUpdate) -> Optional[Menu]:
        menu = await self.get(id)
        if not menu:
            raise HTTPException(status_code=404, detail="Menu not found")

        # 使用 model_dump 来获取更新数据，无视m2m字段
        update_data = menu_in.model_dump(exclude_unset=True, exclude={"buttons"})

        # 先更新非m2m字段
        await menu.update_from_dict(update_data).save()

        # 如果m2m字段存在，单独处理
        if menu_in.buttons:
            await menu.buttons.clear()  # 清空现有的m2m关系
            for button_id in menu_in.buttons:
                button = await Button.get_or_none(id=button_id)
                if button:
                    await menu.buttons.add(button)

        return menu

    async def remove(self, id: int) -> bool:
        menu = await self.get(id)
        if not menu:
            return False
        await menu.delete()
        return True

    async def batch_remove(self, ids: List[int]) -> bool:
        deleted_count = await Menu.filter(id__in=ids).delete()
        return deleted_count == len(ids)

    async def get_first_level_menus(self) -> List[Menu]:
        return await Menu.filter(parent_id=0)

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
