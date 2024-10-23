from typing import List

from app.models.department import Department
from app.schemas.departments import DepartmentCreate, DepartmentUpdate, DepartmentBase
from app.services.base import CRUDBaseService, CreateSchemaType, ModelType
from app.services.user import user_service


class DepartmentService(CRUDBaseService[Department, DepartmentCreate, DepartmentUpdate]):
    def __init__(self):
        super().__init__(Department)

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        manager = await user_service.get(id=obj_in.manager_id)
        if manager:
            obj_in.manager_name = manager.user_name

        return await super().create(obj_in)

    async def update(self, id: int, obj_in: CreateSchemaType) -> ModelType:
        manager = await user_service.get(id=obj_in.manager_id)
        if manager:
            obj_in.manager_name = manager.user_name

        return await super().update(id, obj_in)

    async def get_departments_tree(self, departments: List[Department], parent_id: int = 0) -> List[dict]:
        tree = []  # 初始化树形结构列表
        for department in departments:
            if department.parent_id == parent_id:
                children = await self.get_departments_tree(departments, department.id)  # 递归获取子菜单
                department_dict = await department_service.to_dict(department)
                if children:
                    department_dict["children"] = children
                tree.append(department_dict)
        return tree

    async def to_dict(self, department: Department) -> dict:
        return await Department.to_dict(department, schema=DepartmentBase, m2m=False)


department_service = DepartmentService()
