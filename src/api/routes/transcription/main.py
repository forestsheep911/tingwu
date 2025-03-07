"""转写主路由逻辑"""

from fastapi import APIRouter, BackgroundTasks
from src.api.models import TranscriptionRequest, TaskResponse
from src.client import create_client
from .kintone import get_kintone_file
from .oss import upload_to_oss, generate_signed_url
from .processor import process_task_result
import os
import traceback

router = APIRouter()


@router.post("/process", response_model=TaskResponse)
async def process_transcription(
    request: TranscriptionRequest, background_tasks: BackgroundTasks
):
    """处理转写请求"""
    print(f"Received process request for Record {request.record_id}", flush=True)

    # 直接将整个任务放入后台
    background_tasks.add_task(process_full_task, request)
    print(
        f"Request for Record {request.record_id}: Added to background tasks", flush=True
    )
    return TaskResponse(message="任务已提交，正在后台处理")


async def process_full_task(request: TranscriptionRequest):
    """后台处理完整任务"""
    record_id = request.record_id
    print(f"Starting background task for Record {record_id}", flush=True)
    try:
        # Step 1: 从 Kintone 下载文件
        print(f"Task for Record {record_id}: Downloading file from Kintone", flush=True)
        local_file_path = get_kintone_file(record_id)

        # Step 2: 上传到 OSS
        oss_bucket = "tingwu-media-file-provide"
        oss_object_name = f"tingwu/{record_id}/{os.path.basename(local_file_path)}"
        print(
            f"Task for Record {record_id}: Uploading to OSS as {oss_object_name}",
            flush=True,
        )
        oss_url = upload_to_oss(local_file_path, oss_bucket, oss_object_name)

        # Step 3: 生成签名 URL
        print(f"Task for Record {record_id}: Generating signed URL", flush=True)
        signed_url = generate_signed_url(oss_bucket, oss_object_name, expires=3600)

        # Step 4: 创建 Tingwu 任务
        print(f"Task for Record {record_id}: Creating Tingwu task", flush=True)
        client = create_client()
        response = client.create_offline_task(
            file_url=signed_url,
            source_language=request.language,
            enable_chapters=request.chapters,
            enable_meeting_assistance=request.meeting,
            enable_summarization=request.summary,
        )
        task_id = response.get("Data", {}).get("TaskId")
        if not task_id:
            raise Exception("创建任务失败：未获取到任务ID")

        print(f"Task {task_id}: Created and processing in background", flush=True)

        # Step 5: 处理结果
        await process_task_result(task_id, record_id, oss_url)

    except Exception as e:
        print(f"Background task for Record {record_id} failed: {str(e)}", flush=True)
        print(f"Stack trace: {traceback.format_exc()}", flush=True)
