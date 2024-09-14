from fastapi import APIRouter

from .case import router

router_case = APIRouter()
router_case.include_router(router)
