from typing import List, Optional

from app.models import Menu
from app.schemas.route import RouteCreate, RouteUpdate


class RouteService:
    async def get_routes(self) -> List[Menu]:
        return await Menu.filter(status='1').order_by('order')

    async def create_route(self, route_in: RouteCreate) -> Menu:
        route_data = route_in.model_dump()
        return await Menu.create(**route_data)

    async def update_route(self, route_id: int, route_in: RouteUpdate) -> Optional[Menu]:
        route = await Menu.get_or_none(id=route_id)
        if route:
            await route.update_from_dict(route_in.dict(exclude_unset=True)).save()
        return route

    async def delete_route(self, route_id: int) -> bool:
        route = await Menu.get_or_none(id=route_id)
        if route:
            await route.delete()
            return True
        return False


route_service = RouteService()
