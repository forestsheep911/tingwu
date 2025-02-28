"""API 包"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="听悟 API",
    description="听悟音视频转写服务 API",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from .routes import transcription, task

# 注册路由
app.include_router(transcription.router)
app.include_router(task.router) 