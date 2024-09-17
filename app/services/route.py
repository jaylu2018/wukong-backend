from typing import List

from app.models import Menu
from app.schemas.route import RouteCreate, RouteUpdate
from app.services.base import CRUDBase


class RouteService(CRUDBase[Menu, RouteCreate, RouteUpdate]):
    def __init__(self):
        super().__init__(Menu)

    @staticmethod
    async def get_routes() -> List[Menu]:
        return await Menu.filter(status='1').order_by('order')


route_service = RouteService()
