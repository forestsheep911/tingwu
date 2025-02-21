import json
from typing import Dict, Any, List
from datetime import datetime


class TaskMixin:
    """任务管理相关功能"""

    def create_offline_task(
        self,
        file_url: str,
        source_language: str = "cn",
        enable_diarization: bool = False,
        speaker_count: int = 0,
        enable_translation: bool = False,
        target_languages: List[str] = None,
        enable_chapters: bool = False,
        enable_meeting_assistance: bool = False,
        enable_summarization: bool = False,
        enable_ppt: bool = False,
        enable_text_polish: bool = False,
        dry_run: bool = False,  # 新增 dry-run 参数
    ) -> Dict[str, Any]:
        """创建离线转写任务"""
        body = {
            "AppKey": self.app_key,
            "Input": {
                "FileUrl": file_url,
                "SourceLanguage": source_language,
                "TaskKey": f'task{datetime.now().strftime("%Y%m%d%H%M%S")}',
            },
            "Parameters": {},
        }

        # 设置语音识别参数
        if enable_diarization:
            body["Parameters"]["Transcription"] = {
                "DiarizationEnabled": True,
                "Diarization": {"SpeakerCount": speaker_count},
            }

        # 设置翻译参数
        if enable_translation and target_languages:
            body["Parameters"]["TranslationEnabled"] = True
            body["Parameters"]["Translation"] = {"TargetLanguages": target_languages}

        # 设置其他参数
        if enable_chapters:
            body["Parameters"]["AutoChaptersEnabled"] = True

        if enable_meeting_assistance:
            body["Parameters"]["MeetingAssistanceEnabled"] = True
            body["Parameters"]["MeetingAssistance"] = {
                "Types": ["Actions", "KeyInformation"]
            }

        if enable_summarization:
            body["Parameters"]["SummarizationEnabled"] = True
            body["Parameters"]["Summarization"] = {
                "Types": [
                    "Paragraph",
                    "Conversational",
                    "QuestionsAnswering",
                    "MindMap",
                ]
            }

        if enable_ppt:
            body["Parameters"]["PptExtractionEnabled"] = True

        if enable_text_polish:
            body["Parameters"]["TextPolishEnabled"] = True

        request = self._create_request("/openapi/tingwu/v2/tasks")
        request.add_query_param("type", "offline")
        request.set_content(json.dumps(body).encode("utf-8"))

        # 如果是dry-run模式，打印请求内容并返回空字典
        if dry_run:
            print("Dry Run模式 - 将要发送的请求内容:")
            print(
                f"URL: https://tingwu.cn-beijing.aliyuncs.com/openapi/tingwu/v2/tasks?type=offline"
            )
            print(f"Method: {request.get_method()}")
            print(f"Headers: {dict(request.get_headers())}")
            print(f"Body: {json.dumps(body, indent=2, ensure_ascii=False)}")
            return {}

        # 正常发送请求
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态"""
        request = self._create_request(
            f"/openapi/tingwu/v2/tasks/{task_id}", method="GET"
        )
        response = self.client.do_action_with_exception(request)
        return json.loads(response)
