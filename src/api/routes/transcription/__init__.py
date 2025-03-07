"""转写相关路由模块"""

from fastapi import APIRouter
from .main import router as main_router

router = APIRouter(prefix="/api/v1", tags=["transcription"])

# 注册主路由
router.include_router(main_router)
