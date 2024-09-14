# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime
#
# class CaseBase(BaseModel):
#     title: str
#     description: Optional[str] = None
#     status: str
#
# class CaseCreate(CaseBase):
#     pass
#
# class CaseUpdate(CaseBase):
#     title: Optional[str] = None
#     status: Optional[str] = None
#
# class CaseOut(CaseBase):
#     id: int
#     created_at: datetime
#     updated_at: datetime
#
#     class Config:
#         orm_mode = True
