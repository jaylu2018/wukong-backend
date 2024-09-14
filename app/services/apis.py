from typing import List, Optional
from app.models.api import Api
from app.schemas.apis import ApiCreate, ApiUpdate


class ApiService:

    async def get(self, id: int) -> Api:
        return await Api.get_or_none(id=id)

    async def get_api_by_path_and_method(self, path: str, method: str) -> Optional[Api]:
        return await Api.filter(path=path, method=method).first()

    async def list(self, page: int = 1, page_size: int = 10, order: List[str] = None, **filters) -> tuple[int, List[Api]]:
        if order is None:
            order = []
        query = Api.filter(**filters)
        total = await query.count()
        result = await query.offset((page - 1) * page_size).limit(page_size).order_by(*order)
        return total, result

    async def create(self, obj_in: ApiCreate) -> Api:
        api_data = obj_in.model_dump()
        new_api = Api(**api_data)
        await new_api.save()
        return new_api

    async def update(self, id: int, obj_in: ApiUpdate) -> Api:
        api_data = obj_in.model_dump(exclude_unset=True)
        api_obj = await self.get(id=id)
        for key, value in api_data.items():
            setattr(api_obj, key, value)
        await api_obj.save()
        return api_obj

    async def remove(self, id: int) -> None:
        api_obj = await self.get(id=id)
        await api_obj.delete()

    async def batch_remove(self, ids: List[int]) -> None:
        await Api.filter(id__in=ids).delete()

    async def get_api_tree(self) -> List[dict]:
        apis = await Api.all()
        return self.build_api_tree(apis)

    @staticmethod
    def build_api_tree(apis: List[Api]) -> List[dict]:
        parent_map = {"root": {"id": "root", "children": []}}
        for api in apis:
            tags = api.tags
            parent_id = "root"
            for tag in tags:
                node_id = f"parent${tag}"
                if node_id not in parent_map:
                    node = {"id": node_id, "summary": tag, "children": []}
                    parent_map[node_id] = node
                    parent_map[parent_id]["children"].append(node)
                parent_id = node_id
            parent_map[parent_id]["children"].append({
                "id": api.id,
                "summary": api.summary,
            })
        return parent_map["root"]["children"]

    async def to_dict(self, api: Api) -> dict:
        return await api.to_dict()


api_service = ApiService()
