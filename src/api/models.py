"""API 模型定义"""

from typing import Optional
from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """转写请求模型"""

    record_id: str = Field(..., description="Kintone Record ID")
    language: str = Field("cn", description="源语言，默认为中文(cn)")
    speakers: Optional[int] = Field(
        None, description="说话人数量，0表示不定人数，2表示2人"
    )
    translate: bool = Field(False, description="是否启用翻译功能")
    target_lang: str = Field("en", description="目标翻译语言，默认为英语(en)")
    chapters: bool = Field(False, description="是否启用章节速览")
    meeting: bool = Field(False, description="是否启用会议智能")
    summary: bool = Field(False, description="是否启用摘要功能")
    ppt: bool = Field(False, description="是否启用PPT提取")
    polish: bool = Field(False, description="是否启用口语书面化")


class TaskResponse(BaseModel):
    """任务响应模型"""

    message: str = Field(..., description="响应消息")
