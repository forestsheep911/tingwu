from typing import Optional
import sys
import json
import time
import typer
from rich.console import Console
from src.client import create_client
from src.utils.env import load_env_or_exit
from src.utils.download import download_results
from src.processors.transcription import format_transcription

console = Console()

def process(
    file_url: Optional[str] = typer.Option(
        None, "--url", "-u", help="音视频文件的URL地址"
    ),
    language: str = typer.Option(
        "cn", "--language", "-l", help="源语言，默认为中文(cn)"
    ),
    speakers: Optional[int] = typer.Option(
        None,
        "--speakers",
        "-s",
        help="说话人数量，0表示不定人数，2表示2人，不指定则不启用说话人分离",
        callback=lambda x: (
            x if x in (None, 0, 2) else typer.BadParameter("只能指定 0 或 2")
        ),
    ),
    translate: bool = typer.Option(False, "--translate", "-t", help="是否启用翻译功能"),
    target_lang: str = typer.Option(
        "en", "--target-lang", help="目标翻译语言，默认为英语(en)"
    ),
    chapters: bool = typer.Option(False, "--chapters", "-c", help="是否启用章节速览"),
    meeting: bool = typer.Option(False, "--meeting", "-m", help="是否启用会议智能"),
    summary: bool = typer.Option(False, "--summary", help="是否启用摘要功能"),
    ppt: bool = typer.Option(False, "--ppt", "-p", help="是否启用PPT提取"),
    polish: bool = typer.Option(False, "--polish", help="是否启用口语书面化"),
    wait_time: int = typer.Option(
        1800, "--timeout", help="最大等待时间（秒），默认30分钟"
    ),
    interval: int = typer.Option(30, "--interval", help="查询间隔（秒），默认30秒"),
    output_dir: str = typer.Option("output", "--output", "-o", help="结果保存目录"),
) -> None:
    """一键完成创建任务、等待完成和结果处理"""
    try:
        # 如果命令行没有指定URL，则从环境变量读取
        if not file_url:
            file_url = load_env_or_exit("AUDIO_FILE_URL")
            console.print(f"[blue]从环境变量读取的文件URL: {file_url}[/blue]")
        
        # 创建客户端
        client = create_client()

        # 显示任务配置信息
        console.print("\n[bold]任务配置:[/bold]")
        console.print(f"文件URL: {file_url}")
        console.print(f"源语言: {language}")
        if speakers is not None:
            console.print(f"说话人数: {speakers}")

        # 第一步：创建任务
        with console.status("[bold green]正在创建转写任务...") as status:
            response = client.create_offline_task(
                file_url=file_url,
                source_language=language,
                enable_diarization=speakers is not None,
                speaker_count=speakers if speakers is not None else 0,
                enable_translation=translate,
                target_languages=[target_lang] if translate else None,
                enable_chapters=chapters,
                enable_meeting_assistance=meeting,
                enable_summarization=summary,
                enable_ppt=ppt,
                enable_text_polish=polish,
            )

        # 检查任务创建是否成功
        if "Data" not in response or "TaskId" not in response["Data"]:
            raise Exception("创建任务失败：未获取到任务ID")
        
        task_id = response["Data"]["TaskId"]
        console.print(f"\n[green]任务创建成功！任务ID: {task_id}[/green]")

        # 在开始等待之前稍作暂停，让服务器有时间处理
        time.sleep(5)

        # 第二步：等待任务完成（添加重试机制）
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                with console.status("[bold green]等待任务完成...") as status:
                    result = client.wait_for_task_completion(
                        task_id=task_id,
                        initial_wait=30,
                        timeout=wait_time,
                        interval=interval,
                        output_dir=output_dir,
                    )
                break  # 如果成功，跳出重试循环
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise  # 如果重试次数用完，抛出异常
                console.print(f"[yellow]等待过程中出现错误: {str(e)}[/yellow]")
                console.print(f"[yellow]5秒后进行第{retry_count + 1}次重试...[/yellow]")
                time.sleep(5)

        console.print("[bold green]任务完成！[/bold green]")

        # 第三步：处理结果（也添加重试机制）
        retry_count = 0
        while retry_count < max_retries:
            try:
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
                break  # 如果成功，跳出重试循环
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise  # 如果重试次数用完，抛出异常
                console.print(f"[yellow]处理结果时出现错误: {str(e)}[/yellow]")
                console.print(f"[yellow]5秒后进行第{retry_count + 1}次重试...[/yellow]")
                time.sleep(5)

        console.print("\n[bold green]所有处理已完成！[/bold green]")

    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        console.print("[yellow]提示: 如果任务已创建成功，您可以稍后使用 wait-task 命令查看结果[/yellow]")
        if 'task_id' in locals():
            console.print(f"[yellow]任务ID: {task_id}[/yellow]")
        sys.exit(1) 