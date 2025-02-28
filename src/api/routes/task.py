"""任务相关路由"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
from src.client import create_client
from src.utils import download_results
from src.processors import format_transcription
import json

router = APIRouter(prefix="/api/v1", tags=["task"])

@router.get("/task/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """获取任务状态"""
    try:
        client = create_client()
        response = client.get_task_status(task_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}/result")
async def get_task_result(
    task_id: str,
    output_dir: str = Query("output", description="结果保存目录")
) -> Dict[str, Any]:
    """获取任务结果"""
    try:
        client = create_client()
        result = client.wait_for_task_completion(
            task_id=task_id,
            output_dir=output_dir
        )
        
        if "Data" in result and "Result" in result["Data"]:
            downloaded_files = download_results(result["Data"]["Result"], output_dir)
            
            if "Transcription" in downloaded_files:
                with open(downloaded_files["Transcription"], "r", encoding="utf-8") as f:
                    transcription_data = json.load(f)
                format_transcription(transcription_data, task_id, output_dir)
                
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 