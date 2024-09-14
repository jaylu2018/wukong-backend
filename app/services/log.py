from typing import Any, Dict, List, Optional
from tortoise.expressions import Q

from app.models import Log
from app.models.base import LogType, LogDetailType


class LogService:
    async def create(self, log_type: LogType, log_detail_type: LogDetailType, by_user_id: int) -> Log:
        return await Log.create(log_type=log_type, log_detail_type=log_detail_type, by_user_id=by_user_id)

    async def get(self, log_id: int) -> Optional[Log]:
        return await Log.get_or_none(id=log_id)

    async def list_logs(
        self, page: int = 1, page_size: int = 10, filters: Dict[str, Any] = None
    ) -> tuple[int, List[Log]]:
        query = Log.all()
        if filters:
            query = query.filter(**filters)
        total = await query.count()
        logs = await query.offset((page - 1) * page_size).limit(page_size)
        return total, [await log.to_dict() for log in logs]

    async def update(self, log_id: int, obj_in: Dict[str, Any]) -> Optional[Log]:
        log = await self.get(log_id)
        if not log:
            return None
        await log.update_from_dict(obj_in)
        await log.save()
        return log

    async def delete(self, log_id: int) -> bool:
        log = await self.get(log_id)
        if log:
            await log.delete()
            return True
        return False


log_service = LogService()