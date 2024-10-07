from typing import List

from app.models import Log
from app.schemas.logs import LogCreate, LogUpdate
from app.services.base import CRUDBaseService


class LogService(CRUDBaseService[Log, LogCreate, LogUpdate]):
    def __init__(self):
        super().__init__(Log)

    async def to_dict(self):
        ...


log_service = LogService()
