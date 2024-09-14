from typing import List, Optional
from tortoise.expressions import Q

from app.models import Log
from app.models.base import LogType, LogDetailType


class LogService:

    async def create(self, log_type: LogType, log_detail_type: LogDetailType, by_user_id: int) -> Log:
        return await Log.create(log_type=log_type, log_detail_type=log_detail_type, by_user_id=by_user_id)

    async def get(self, id: int) -> Optional[Log]:
        return await Log.get_or_none(id=id)

    async def list(self, page: int = 1, page_size: int = 10, search: Q = None, order: List[str] = None):
        query = Log.all()
        if search:
            query = query.filter(search)
        if order:
            query = query.order_by(*order)
        total = await query.count()
        logs = await query.offset((page - 1) * page_size).limit(page_size)
        return total, logs

    async def update(self, log_id: int, obj_in: dict) -> Optional[Log]:
        log = await Log.get(id=log_id)
        if not log:
            return None
        for field, value in obj_in.items():
            setattr(log, field, value)
        await log.save()
        return log

    async def remove(self, id: int):
        log = await Log.get(id=id)
        await log.delete()

    async def to_dict(self, log: Log, exclude_fields: List[str] = None):
        return await log.to_dict(exclude_fields=exclude_fields)


log_service = LogService()
