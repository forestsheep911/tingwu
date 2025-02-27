from typing import Optional, List
import sys
import typer
from rich.console import Console
from src.client import create_client
from src.utils import load_env_or_exit, print_response

console = Console()

def create_task(
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
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="仅打印请求内容，不发送请求"
    ),
) -> None:
    """创建听悟离线转写任务"""
    try:
        # 如果命令行没有指定URL，则从环境变量读取
        if not file_url:
            file_url = load_env_or_exit("AUDIO_FILE_URL")
        # 创建客户端
        client = create_client()

        # 显示任务配置信息
        console.print("\n[bold]任务配置:[/bold]")
        console.print(f"文件URL: {file_url}")
        console.print(f"源语言: {language}")
        if speakers is not None:  # 只在指定 speakers 时显示
            console.print(f"说话人数: {speakers}")
        console.print(f"Dry Run模式: {dry_run}")

        # 创建任务
        with console.status("[bold green]正在创建转写任务...") as status:
            response = client.create_offline_task(
                file_url=file_url,
                source_language=language,
                enable_diarization=speakers is not None,  # 如果指定了 speakers，则启用
                speaker_count=(
                    speakers if speakers is not None else 0
                ),  # 如果未指定，传 0（但不会生效）
                enable_translation=translate,
                target_languages=[target_lang] if translate else None,
                enable_chapters=chapters,
                enable_meeting_assistance=meeting,
                enable_summarization=summary,
                enable_ppt=ppt,
                enable_text_polish=polish,
                dry_run=dry_run,
            )

        # 如果不是dry-run模式，打印响应
        if not dry_run:
            print_response(response)
        else:
            console.print(
                "[yellow]Dry Run模式已启用，仅打印请求内容，未实际发送请求[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        sys.exit(1) 