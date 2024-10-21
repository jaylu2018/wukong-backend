from app.models import Menu
from app.schemas.menus import MenuOut
from app.schemas.route import RouteCreate, RouteUpdate
from app.services.base import CRUDBaseService


class RouteService(CRUDBaseService[Menu, RouteCreate, RouteUpdate]):
    def __init__(self):
        super().__init__(Menu)

    async def to_dict(self, menu: Menu) -> dict:
        return await Menu.to_dict(menu, schema=MenuOut, m2m=False)


route_service = RouteService()
