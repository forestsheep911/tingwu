# src/result_processing.py
import json
import requests
from pathlib import Path
from typing import Dict, Any
from rich.console import Console

console = Console()


def download_results(results: Dict[str, str], output_dir: str) -> None:
    """下载转写结果文件"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for key, url in results.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            file_name = url.split("/")[-1].split("?")[0]
            file_path = output_path / file_name
            with open(file_path, "wb") as file:
                file.write(response.content)
            console.print(f"[green]已下载 {key}: {file_path}[/green]")
        except Exception as e:
            console.print(f"[red]下载 {key} 失败: {e}[/red]")


def format_transcription(result: Dict[str, Any], task_id: str, output_dir: str) -> None:
    """格式化转写结果，按时间顺序排列并按发言人分隔"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if "Transcription" not in result or "Paragraphs" not in result["Transcription"]:
        console.print("[red]错误: 结果中没有 Transcription.Paragraphs 数据[/red]")
        return

    paragraphs = result["Transcription"]["Paragraphs"]

    # 提取所有单词并按时间排序
    all_words = []
    for para in paragraphs:
        speaker_id = para["SpeakerId"]
        for word in para["Words"]:
            all_words.append(
                {
                    "SpeakerId": speaker_id,
                    "Start": word["Start"],
                    "End": word["End"],
                    "Text": word["Text"],
                }
            )
    all_words.sort(key=lambda x: x["Start"])

    # 按时间顺序处理
    output_lines = []
    current_speaker = None
    current_text = ""
    current_start = None

    for word in all_words:
        speaker = word["SpeakerId"]
        text = word["Text"]
        if speaker != current_speaker and current_speaker is not None:
            output_lines.append(f"发言人{current_speaker} {format_time(current_start)}")
            output_lines.append(current_text.strip())
            current_text = text
            current_start = word["Start"]
            current_speaker = speaker
        elif current_speaker is None:
            current_speaker = speaker
            current_text = text
            current_start = word["Start"]
        else:
            current_text += text

    if current_speaker is not None:
        output_lines.append(f"发言人{current_speaker} {format_time(current_start)}")
        output_lines.append(current_text.strip())

    # 打印和保存
    console.print("\n[bold green]格式化转写结果:[/bold green]")
    for line in output_lines:
        console.print(line)

    output_file = output_path / f"task_{task_id}_formatted.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    console.print(f"\n[green]格式化结果已保存到: {output_file}[/green]")


def format_time(ms: int) -> str:
    """将毫秒转换为 [mm:ss] 格式"""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"[{minutes:02d}:{seconds:02d}]"
