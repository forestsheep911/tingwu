import time
import json
from typing import Dict, Any, Optional
from pathlib import Path
from rich.console import Console


class ResultMixin:
    """结果处理相关功能"""

    def wait_for_task_completion(
        self,
        task_id: str,
        initial_wait: int = 0,
        interval: int = 30,
        timeout: int = 1800,
        output_dir: Optional[str] = None,
    ) -> Dict[str, Any]:
        """等待任务完成并获取结果"""
        if initial_wait > 0:
            time.sleep(initial_wait)

        start_time = time.time()
        console = Console()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"等待任务完成超时（{timeout}秒）")

            response = self.get_task_status(task_id)
            # 打印完整的响应内容
            console.print("\n[bold blue]查询响应:[/bold blue]")
            console.print(response)
            
            status = response.get("Data", {}).get("TaskStatus", "")
            console.print(f"\n当前状态: {status}")

            if status == "COMPLETED":
                if output_dir:
                    self._save_task_result(response, task_id, output_dir)
                return response
            elif status == "FAILED":
                error_msg = response.get("Message", "未知错误")
                error_code = response.get("Code", "未知错误码")
                raise Exception(f"任务失败: {error_msg} (错误码: {error_code})")
            elif status == "CANCELLED":
                raise Exception("任务已被取消")
            elif not status:  # 如果状态为空
                console.print("[yellow]警告: 响应中没有任务状态信息[/yellow]")
                console.print(f"完整响应: {response}")

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
