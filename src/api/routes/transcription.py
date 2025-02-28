"""转写相关路由"""
from fastapi import APIRouter, HTTPException
from src.api.models import TranscriptionRequest, TaskResponse
from src.client import create_client
from src.utils.env import load_env_or_exit

router = APIRouter(prefix="/api/v1", tags=["transcription"])

@router.post("/transcribe", response_model=TaskResponse)
async def create_transcription(request: TranscriptionRequest):
    """创建转写任务"""
    try:
        # 如果没有指定URL，从环境变量读取
        file_url = request.file_url
        if not file_url:
            file_url = load_env_or_exit("AUDIO_FILE_URL")
            
        client = create_client()
        response = client.create_offline_task(
            file_url=file_url,
            source_language=request.language,
            enable_diarization=request.speakers is not None,
            speaker_count=request.speakers if request.speakers is not None else 0,
            enable_translation=request.translate,
            target_languages=[request.target_lang] if request.translate else None,
            enable_chapters=request.chapters,
            enable_meeting_assistance=request.meeting,
            enable_summarization=request.summary,
            enable_ppt=request.ppt,
            enable_text_polish=request.polish,
        )
        
        task_id = response.get("Data", {}).get("TaskId")
        if not task_id:
            raise HTTPException(status_code=500, detail="创建任务失败：未获取到任务ID")
            
        return TaskResponse(
            task_id=task_id,
            message="任务创建成功"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 