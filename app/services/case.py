# from typing import List, Optional
#
# from app.models import Case
# from app.schemas.case import CaseCreate, CaseUpdate
#
#
# class CaseService:
#     async def get_cases(self, page: int = 1, page_size: int = 10) -> tuple[int, List[Case]]:
#         total = await Case.all().count()
#         cases = await Case.all().offset((page - 1) * page_size).limit(page_size)
#         return total, cases
#
#     async def get_case(self, case_id: int) -> Optional[Case]:
#         return await Case.get_or_none(id=case_id)
#
#     async def create_case(self, case_in: CaseCreate) -> Case:
#         case_data = case_in.dict()
#         return await Case.create(**case_data)
#
#     async def update_case(self, case_id: int, case_in: CaseUpdate) -> Optional[Case]:
#         case = await Case.get_or_none(id=case_id)
#         if case:
#             await case.update_from_dict(case_in.dict(exclude_unset=True)).save()
#         return case
#
#     async def delete_case(self, case_id: int) -> bool:
#         case = await Case.get_or_none(id=case_id)
#         if case:
#             await case.delete()
#             return True
#         return False
#
#
# case_service = CaseService()
