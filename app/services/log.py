from typing import List

from app.models import Log
from app.schemas.logs import LogCreate, LogUpdate
from app.services.base import CRUDBase


class LogService(CRUDBase[Log, LogCreate, LogUpdate]):
    def __init__(self):
        super().__init__(Log)

    async def to_dict(self, obj: Log, exclude_fields: List[str] = None) -> dict:
        data = await super().to_dict(obj, exclude_fields=exclude_fields)
        return data


log_service = LogService()
