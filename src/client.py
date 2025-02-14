#!/usr/bin/env python
# coding=utf-8

import os
import json
import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
import time


class TingwuClient:
    def __init__(self, access_key_id: str, access_key_secret: str, app_key: str):
        """初始化听悟客户端

        Args:
            access_key_id: 阿里云访问密钥ID
            access_key_secret: 阿里云访问密钥密码
            app_key: 听悟应用的AppKey
        """
        self.app_key = app_key
        credentials = AccessKeyCredential(access_key_id, access_key_secret)
        self.client = AcsClient(region_id="cn-beijing", credential=credentials)

    def _create_request(self, uri: str, method: str = "PUT") -> CommonRequest:
        """创建通用请求对象"""
        request = CommonRequest()
        request.set_accept_format("json")
        request.set_domain("tingwu.cn-beijing.aliyuncs.com")
        request.set_version("2023-09-30")
        request.set_protocol_type("https")
        request.set_method(method)
        request.set_uri_pattern(uri)
        request.add_header("Content-Type", "application/json")
        return request

    def create_offline_task(
        self,
        file_url: str,
        source_language: str = "cn",
        enable_diarization: bool = False,
        speaker_count: int = 0,
        enable_translation: bool = False,
        target_languages: list = None,
        enable_chapters: bool = False,
        enable_meeting_assistance: bool = False,
        enable_summarization: bool = False,
        enable_ppt: bool = False,
        enable_text_polish: bool = False,
    ) -> Dict[str, Any]:
        """创建离线转写任务

        Args:
            file_url: 音视频文件的URL地址
            source_language: 源语言，默认中文(cn)
            enable_diarization: 是否启用说话人分离
            speaker_count: 说话人数量
            enable_translation: 是否启用翻译
            target_languages: 目标翻译语言列表
            enable_chapters: 是否启用章节速览
            enable_meeting_assistance: 是否启用会议智能
            enable_summarization: 是否启用摘要功能
            enable_ppt: 是���启用PPT提取
            enable_text_polish: 是否启用口语书面化

        Returns:
            Dict: 包含任务ID等信息的响应
        """
        # 构建请求体
        body = {
            "AppKey": self.app_key,
            "Input": {
                "FileUrl": file_url,
                "SourceLanguage": source_language,
                "TaskKey": f'task{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}',
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

        # 设置章节速览
        if enable_chapters:
            body["Parameters"]["AutoChaptersEnabled"] = True

        # 设置会议智能
        if enable_meeting_assistance:
            body["Parameters"]["MeetingAssistanceEnabled"] = True
            body["Parameters"]["MeetingAssistance"] = {
                "Types": ["Actions", "KeyInformation"]
            }

        # 设置摘要功能
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

        # 设置PPT提取
        if enable_ppt:
            body["Parameters"]["PptExtractionEnabled"] = True

        # 设置口语书面化
        if enable_text_polish:
            body["Parameters"]["TextPolishEnabled"] = True

        # 创建并发送请求
        request = self._create_request("/openapi/tingwu/v2/tasks")
        request.add_query_param("type", "offline")
        request.set_content(json.dumps(body).encode("utf-8"))

        try:
            response = self.client.do_action_with_exception(request)
            return json.loads(response)
        except Exception as e:
            raise Exception(f"创建任务失败: {str(e)}")

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            Dict: 包含任务状态的响应
        """
        request = self._create_request(
            f"/openapi/tingwu/v2/tasks/{task_id}", method="GET"
        )
        response = self.client.do_action_with_exception(request)
        return json.loads(response)

    def wait_for_task_completion(
        self,
        task_id: str,
        initial_wait: int = 30,
        interval: int = 30,
        timeout: int = 1800,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """等待任务完成并获取结果

        Args:
            task_id: 任务ID
            initial_wait: 首次查询前等待时间（秒）
            interval: 轮询间隔（秒）
            timeout: 最大等待时间（秒）
            output_dir: 结果保存目录，默认为 'output'

        Returns:
            Dict: 任务结果
        """
        # 首次等待
        time.sleep(initial_wait)

        start_time = time.time()

        while True:
            # 检查是否超时
            if time.time() - start_time > timeout:
                raise TimeoutError(f"等待任务完成超时（{timeout}秒）")

            # 查询任务状态
            response = self.get_task_status(task_id)

            # 获取任务状态
            status = response.get("Data", {}).get("TaskStatus", "")

            # 根据状态处理
            if status == "COMPLETED":
                # 任务完成，保存结果
                if output_dir:
                    self._save_task_result(response, task_id, output_dir)
                return response
            elif status == "FAILED":
                raise Exception(f"任务失败: {response.get('Message', '未知错误')}")
            elif status == "CANCELLED":
                raise Exception("任务已被取消")

            # 等待下次查询
            time.sleep(interval)

    def _save_task_result(
        self, result: Dict[str, Any], task_id: str, output_dir: str
    ) -> None:
        """保存任务结果到文件

        Args:
            result: 任务结果
            task_id: 任务ID
            output_dir: 输出目录
        """
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存完整结果
        result_file = output_path / f"task_{task_id}_result.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 如果有转写文本，单独保存
        if "Sentences" in result.get("Data", {}):
            text_file = output_path / f"task_{task_id}_text.txt"
            sentences = result["Data"]["Sentences"]
            with open(text_file, "w", encoding="utf-8") as f:
                for sentence in sentences:
                    f.write(f"{sentence.get('Text', '')}\n")


def main():
    # 加载环境变量
    load_dotenv()

    # 初始化客户端
    client = TingwuClient(
        access_key_id=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
        app_key=os.getenv("TINGWU_APP_KEY"),
    )

    # 创建任务示例
    try:
        response = client.create_offline_task(
            file_url="您的音频文件URL",
            enable_diarization=True,
            speaker_count=2,
            enable_translation=True,
            target_languages=["en"],
            enable_chapters=True,
            enable_meeting_assistance=True,
            enable_summarization=True,
        )
        print("响应结果:")
        print(json.dumps(response, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()
