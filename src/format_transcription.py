import json
from pathlib import Path
from typing import List, Any
from rich.console import Console

console = Console()


def format_time(ms: int) -> str:
    """将毫秒转换为 [mm:ss] 格式"""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"[{minutes:02d}:{seconds:02d}]"


def process_transcription(json_file: str, output_dir: str = "output") -> None:
    """处理转写结果，按时间顺序排列并按发言人分隔输出"""
    try:
        # 读取 JSON 文件
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 检查是否有 Transcription 数据
        if "Transcription" not in data or "Paragraphs" not in data["Transcription"]:
            console.print(
                "[red]错误: JSON 文件中没有 Transcription.Paragraphs 数据[/red]"
            )
            return

        paragraphs = data["Transcription"]["Paragraphs"]

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
        all_words.sort(key=lambda x: x["Start"])  # 按 Start 时间排序

        # 按时间顺序处理，动态切换发言人
        output_lines = []
        current_speaker = None
        current_text = ""
        current_start = None

        for word in all_words:
            speaker = word["SpeakerId"]
            text = word["Text"]

            if speaker != current_speaker and current_speaker is not None:
                # 发言人切换，保存上一段
                output_lines.append(
                    f"发言人{current_speaker} {format_time(current_start)}"
                )
                output_lines.append(current_text.strip())
                current_text = text
                current_start = word["Start"]
                current_speaker = speaker
            elif current_speaker is None:
                # 第一个词
                current_speaker = speaker
                current_text = text
                current_start = word["Start"]
            else:
                # 同一发言人，追加文本
                current_text += text

        # 保存最后一段
        if current_speaker is not None:
            output_lines.append(f"发言人{current_speaker} {format_time(current_start)}")
            output_lines.append(current_text.strip())

        # 打印到控制台
        console.print("\n[bold green]转写结果:[/bold green]")
        for line in output_lines:
            console.print(line)

        # 保存到文件
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / f"task_{data['TaskId']}_formatted.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))
        console.print(f"\n[green]结果已保存到: {output_file}[/green]")

    except FileNotFoundError:
        console.print(f"[red]错误: 文件 {json_file} 不存在[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]错误: {json_file} 不是有效的 JSON 文件[/red]")
    except Exception as e:
        console.print(f"[red]处理失败: {str(e)}[/red]")


def main():
    import sys

    if len(sys.argv) != 2:
        console.print(
            "[red]用法: poetry run python format_transcription.py <json文件路径>[/red]"
        )
        sys.exit(1)

    json_file = sys.argv[1]
    process_transcription(json_file)


if __name__ == "__main__":
    main()
