"""转写结果处理器"""
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from src.utils import format_time

console = Console()

def format_transcription(result: Dict[str, Any], task_id: str, output_dir: str) -> None:
    """格式化转写结果，按时间顺序排列并按发言人分隔"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if "Transcription" not in result or "Paragraphs" not in result["Transcription"]:
        console.print("[red]错误: 结果中没有 Transcription.Paragraphs 数据[/red]")
        return

    paragraphs = result["Transcription"]["Paragraphs"]
    all_words = []
    
    # 提取所有单词
    for para in paragraphs:
        speaker_id = para["SpeakerId"]
        for word in para["Words"]:
            all_words.append({
                "SpeakerId": speaker_id,
                "Start": word["Start"],
                "End": word["End"],
                "Text": word["Text"],
            })
    all_words.sort(key=lambda x: x["Start"])

    # 格式化输出
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

    # 保存结果
    output_file = output_path / f"task_{task_id}_formatted.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        console.print(f"\n[green]格式化结果已保存到: {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]保存格式化文件失败: {str(e)}[/red]") 