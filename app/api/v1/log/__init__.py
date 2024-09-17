from fastapi import APIRouter

from .logs import router

router_log = APIRouter()
router_log.include_router(router)
