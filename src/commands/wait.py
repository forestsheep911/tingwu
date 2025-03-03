import sys
import json
import typer
from rich.console import Console
from src.client import create_client
from src.utils import print_response, download_results
from src.processors import format_transcription

console = Console()

def wait_task(
    task_id: str = typer.Option(..., "--task-id", "-t", help="要查询的任务ID"),
    wait_time: int = typer.Option(
        1800, "--timeout", help="最大等待时间（秒），默认30分钟"
    ),
    interval: int = typer.Option(30, "--interval", help="查询间隔（秒），默认30秒"),
    output_dir: str = typer.Option("output", "--output", "-o", help="结果保存目录"),
) -> None:
    """等待任务完成并获取结果，自动下载和格式化"""
    try:
        client = create_client()

        with console.status("[bold green]等待任务完成...") as status:
            try:
                result = client.wait_for_task_completion(
                    task_id=task_id,
                    timeout=wait_time,
                    interval=interval,
                    output_dir=output_dir,
                )
                # 打印原始响应内容，帮助调试
                console.print("\n[bold blue]原始响应:[/bold blue]")
                console.print(result)
            except Exception as e:
                console.print("\n[bold red]等待过程中发生错误:[/bold red]")
                console.print(f"错误类型: {type(e).__name__}")
                console.print(f"错误信息: {str(e)}")
                if hasattr(e, 'response'):
                    console.print("\n[bold blue]API响应内容:[/bold blue]")
                    try:
                        console.print(e.response.json())
                    except:
                        console.print(e.response.text)
                raise

        console.print("[bold green]任务完成！[/bold green]")
        print_response(result)

        if "Data" in result and "Result" in result["Data"]:
            console.print("\n[bold green]开始下载结果文件...[/bold green]")
            downloaded_files = download_results(result["Data"]["Result"], output_dir)

            if "Transcription" in downloaded_files:
                console.print("\n[bold green]开始格式化转写结果...[/bold green]")
                with open(downloaded_files["Transcription"], "r", encoding="utf-8") as f:
                    transcription_data = json.load(f)
                format_transcription(transcription_data, task_id, output_dir)
            else:
                console.print("[yellow]警告: 未下载到 Transcription 文件[/yellow]")
        else:
            console.print("[yellow]警告: 结果中没有 Result 数据[/yellow]")

    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        sys.exit(1) 