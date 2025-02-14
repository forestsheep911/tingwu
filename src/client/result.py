import time
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ResultMixin:
    """结果处理相关功能"""

    def wait_for_task_completion(
        self,
        task_id: str,
        initial_wait: int = 30,
        interval: int = 30,
        timeout: int = 1800,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """等待任务完成并获取结果"""
        time.sleep(initial_wait)

        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"等待任务完成超时（{timeout}秒）")

            response = self.get_task_status(task_id)
            status = response.get("Data", {}).get("TaskStatus", "")

            if status == "COMPLETED":
                if output_dir:
                    self._save_task_result(response, task_id, output_dir)
                return response
            elif status == "FAILED":
                raise Exception(f"任务失败: {response.get('Message', '未知错误')}")
            elif status == "CANCELLED":
                raise Exception("任务已被取消")

            time.sleep(interval)

    def _save_task_result(
        self, result: Dict[str, Any], task_id: str, output_dir: str
    ) -> None:
        """保存任务结果到文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存完整结果
        result_file = output_path / f"task_{task_id}_result.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 保存纯文本结果
        if "Sentences" in result.get("Data", {}):
            text_file = output_path / f"task_{task_id}_text.txt"
            sentences = result["Data"]["Sentences"]
            with open(text_file, "w", encoding="utf-8") as f:
                for sentence in sentences:
                    f.write(f"{sentence.get('Text', '')}\n")
