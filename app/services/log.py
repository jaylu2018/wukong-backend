from app.models import Log
from app.schemas.logs import LogCreate, LogUpdate, BaseLog
from app.services.base import CRUDBaseService


class LogService(CRUDBaseService[Log, LogCreate, LogUpdate]):
    def __init__(self):
        super().__init__(Log)

    async def to_dict(self, log: Log) -> dict:
        return await Log.to_dict(log, schema=BaseLog, m2m=False)


log_service = LogService()
