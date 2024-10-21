from typing import List

from app.models.department import Department
from app.schemas.departments import DepartmentCreate, DepartmentUpdate, DepartmentBase
from app.services.base import CRUDBaseService


class DepartmentService(CRUDBaseService[Department, DepartmentCreate, DepartmentUpdate]):
    def __init__(self):
        super().__init__(Department)

    async def get_departments_tree(self) -> List[dict]:
        # 获取所有部门并按顺序排序
        departments = await self.model.all().order_by('order')
        # 创建一个部门字典，键为部门ID，值为部门信息字典
        dept_dict = {dept.id: await self.to_dict(dept) for dept in departments}
        print(dept_dict)

        # 初始化树形结构列表
        tree = []

        # 构建父子关系
        for dept in departments:
            dept_id = dept.id
            parent_id = dept.parent_id
            dept_info = dept_dict[dept_id]

            if parent_id == 0 or parent_id not in dept_dict:
                # 如果是顶级部门或父部门不存在，直接添加到树中
                tree.append(dept_info)
            else:
                # 如果有父部门，将当前部门添加到父部门的children列表中
                parent_dept = dept_dict[parent_id]
                if 'children' not in parent_dept:
                    parent_dept['children'] = []
                parent_dept['children'].append(dept_info)
        return tree

    async def to_dict(self, department: Department) -> dict:
        return await Department.to_dict(department, schema=DepartmentBase, m2m=False)


department_service = DepartmentService()
