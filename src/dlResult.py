import os
import json
import requests
from pathlib import Path
from rich.console import Console

console = Console()


def download_results(results, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    for key, url in results.items():
        try:
            response = requests.get(url)
            response.raise_for_status()  # 如果请求不成功会抛出异常

            # 使用URL中的文件名保存文件
            file_name = url.split("/")[-1].split("?")[0]
            file_path = output_dir / file_name

            with open(file_path, "wb") as file:
                file.write(response.content)

            console.print(f"[green]已下载 {key}: {file_path}[/green]")
        except Exception as e:
            console.print(f"[red]下载 {key} 失败: {e}[/red]")


def main(json_file, output_dir="output"):
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            response = json.load(file)

        if "Data" in response and "Result" in response["Data"]:
            download_results(response["Data"]["Result"], output_dir)
        else:
            console.print("[yellow]警告: 没有找到Result信息。[/yellow]")
    except FileNotFoundError:
        console.print(f"[red]错误: 未找到文件 {json_file}[/red]")
    except json.JSONDecodeError:
        console.print(f"[red]错误: {json_file} 不是有效的JSON文件[/red]")
    except Exception as e:
        console.print(f"[red]未知错误: {e}[/red]")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        console.print("[red]用法: poetry run python dlResult.py <json文件路径>[/red]")
        sys.exit(1)

    json_file = sys.argv[1]
    main(json_file)
