from typing import List, Optional
from app.models.api import Api
from app.schemas.apis import ApiCreate, ApiUpdate
from app.services.base import CRUDBaseService


class ApiService(CRUDBaseService[Api, ApiCreate, ApiUpdate]):
    def __init__(self):
        super().__init__(Api)

    async def get_api_by_path_and_method(self, path: str, method: str) -> Optional[Api]:
        return await self.model.filter(path=path, method=method).first()

    async def get_api_tree(self) -> List[dict]:
        apis = await self.model.all()
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

    async def to_dict(self):
        ...


api_service = ApiService()
