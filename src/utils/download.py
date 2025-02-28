"""下载工具"""
import requests
from pathlib import Path
from typing import Dict
from rich.console import Console

console = Console()

def download_results(results: Dict[str, str], output_dir: str) -> Dict[str, str]:
    """下载转写结果文件，并返回下载文件路径"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    downloaded_files = {}

    for key, url in results.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            file_name = url.split("/")[-1].split("?")[0]
            file_path = output_path / file_name
            with open(file_path, "wb") as file:
                file.write(response.content)
            console.print(f"[green]已下载 {key}: {file_path}[/green]")
            downloaded_files[key] = str(file_path)
        except Exception as e:
            console.print(f"[red]下载 {key} 失败: {e}[/red]")
    return downloaded_files 