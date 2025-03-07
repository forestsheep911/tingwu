"""后台任务处理逻辑"""

import requests
import json
from typing import Dict, Any, List, Optional
import traceback
from src.client import create_client
from src.utils.output import format_time
from src.utils.download import download_results

KINTONE_API_URL = "https://2water.cybozu.com/k/v1"
KINTONE_API_TOKEN = "QPtwOxPEBOs5TBbvb3cieeF9BbMRIilgPx3d9pLv"
KINTONE_APP_ID = "8"

task_execution_count = {}


def update_kintone_record(task_id: str, record_id: str, result_data: Dict[str, Any]):
    """更新 Kintone 记录"""
    print(
        f"Task {task_id}: Starting Kintone update process for Record {record_id}...",
        flush=True,
    )
    headers = {
        "X-Cybozu-API-Token": KINTONE_API_TOKEN,
        "Content-Type": "application/json",
    }

    formatted_transcription = "\n".join(
        f"{item['start_time']} {item['speaker']}: {item['text']}"
        for item in result_data.get("transcription", [])
    )
    auto_chapters = "\n".join(
        f"{format_time(chapter['Start'])} - {format_time(chapter['End'])}: {chapter.get('Headline', '无标题')}\n{chapter.get('Summary', '无摘要')}"
        for chapter in result_data.get("chapters", [])
    )
    summarization = ""
    if "summary" in result_data and result_data["summary"]:
        summary_parts = []
        if "ParagraphSummary" in result_data["summary"]:
            summary_parts.append(
                f"段落摘要: {result_data['summary']['ParagraphSummary']}"
            )
        if "ConversationalSummary" in result_data["summary"]:
            conv_summary = "\n".join(
                f"{item['SpeakerName']}: {item['Summary']}"
                for item in result_data["summary"]["ConversationalSummary"]
            )
            summary_parts.append(f"对话摘要:\n{conv_summary}")
        summarization = "\n\n".join(summary_parts)
    meeting_assistance = ""
    if "meeting_assistance" in result_data and result_data["meeting_assistance"]:
        meeting_parts = []
        if "Keywords" in result_data["meeting_assistance"]:
            keywords = ", ".join(result_data["meeting_assistance"]["Keywords"])
            meeting_parts.append(f"关键词: {keywords}")
        if "Classifications" in result_data["meeting_assistance"]:
            classifications = "\n".join(
                f"{key}: {value:.2%}"
                for key, value in result_data["meeting_assistance"][
                    "Classifications"
                ].items()
            )
            meeting_parts.append(f"分类:\n{classifications}")
        meeting_assistance = "\n".join(meeting_parts)

    payload = {
        "app": KINTONE_APP_ID,
        "id": record_id,
        "record": {
            "formatted_transcription": {"value": formatted_transcription},
            "auto_chapters": {"value": auto_chapters},
            "summarization": {"value": summarization},
            "meeting_assistance": {"value": meeting_assistance},
            "oss_url": {"value": result_data.get("oss_url", "")},
        },
    }
    response = requests.put(
        f"{KINTONE_API_URL}/record.json", headers=headers, json=payload, timeout=10
    )
    response.raise_for_status()
    print(
        f"Task {task_id}: Kintone update successful for Record {record_id}. Response: {response.text}",
        flush=True,
    )


async def process_task_result(task_id: str, record_id: str, oss_url: str):
    """处理 Tingwu 任务结果"""
    if task_id in task_execution_count:
        task_execution_count[task_id] += 1
    else:
        task_execution_count[task_id] = 1
    print(
        f"Task {task_id}: Background task started (Execution #{task_execution_count[task_id]})",
        flush=True,
    )
    if task_execution_count[task_id] > 1:
        print(f"Task {task_id}: Task already processed, skipping...", flush=True)
        return

    try:
        client = create_client()
        result = client.wait_for_task_completion(
            task_id=task_id, initial_wait=5, interval=10, timeout=3600
        )

        downloaded_files = download_results(result["Data"]["Result"], "temp")

        transcription = None
        if "Transcription" in downloaded_files:
            with open(downloaded_files["Transcription"], "r", encoding="utf-8") as f:
                transcription_data = json.load(f)
            paragraphs = transcription_data.get("Transcription", {}).get(
                "Paragraphs", []
            )
            all_words = [
                {
                    "SpeakerId": para["SpeakerId"],
                    "Start": word["Start"],
                    "End": word["End"],
                    "Text": word["Text"],
                }
                for para in paragraphs
                for word in para["Words"]
            ]
            all_words.sort(key=lambda x: x["Start"])
            transcription = []
            current_speaker, current_text, current_start = None, "", None
            for word in all_words:
                speaker = word["SpeakerId"]
                text = word["Text"]
                if speaker != current_speaker and current_speaker is not None:
                    transcription.append(
                        {
                            "speaker": f"发言人{speaker}",
                            "start_time": format_time(current_start),
                            "text": current_text.strip(),
                        }
                    )
                    current_text = text
                    current_start = word["Start"]
                    current_speaker = speaker
                elif current_speaker is None:
                    current_speaker = speaker
                    current_text = text
                    current_start = word["Start"]
                else:
                    current_text += text
            if current_speaker:
                transcription.append(
                    {
                        "speaker": f"发言人{speaker}",
                        "start_time": format_time(current_start),
                        "text": current_text.strip(),
                    }
                )

        chapters = None
        if "AutoChapters" in downloaded_files:
            with open(downloaded_files["AutoChapters"], "r", encoding="utf-8") as f:
                chapters = json.load(f).get("AutoChapters", [])

        summary = None
        if "Summarization" in downloaded_files:
            with open(downloaded_files["Summarization"], "r", encoding="utf-8") as f:
                summary = json.load(f).get("Summarization", {})

        meeting_assistance = None
        if "MeetingAssistance" in downloaded_files:
            with open(
                downloaded_files["MeetingAssistance"], "r", encoding="utf-8"
            ) as f:
                meeting_assistance = json.load(f).get("MeetingAssistance", {})

        result_data = {
            "task_id": task_id,
            "status": "completed",
            "transcription": transcription or [],
            "chapters": chapters or [],
            "summary": summary or {},
            "meeting_assistance": meeting_assistance or {},
            "oss_url": oss_url,
        }
        update_kintone_record(task_id, record_id, result_data)
        print(f"Task {task_id}: Background task completed successfully", flush=True)

    except Exception as e:
        print(
            f"Task {task_id}: Background task failed with error: {str(e)}", flush=True
        )
        print(f"Task {task_id}: Stack trace: {traceback.format_exc()}", flush=True)
