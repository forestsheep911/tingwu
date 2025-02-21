# src/main.py
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from dotenv import load_dotenv

from client import TingwuClient
from utils import load_env_or_exit, print_response
from result_processing import download_results, format_transcription  # 新增导入

app = typer.Typer()
console = Console()


def create_client() -> TingwuClient:
    """创建并返回TingwuClient实例"""
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / ".env"
    if not load_dotenv(env_path, override=True):
        console.print(f"[yellow]警告: 无法加载环境变量文件: {env_path}[/yellow]")
    access_key_id = load_env_or_exit("ALIBABA_CLOUD_ACCESS_KEY_ID")
    access_key_secret = load_env_or_exit("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    app_key = load_env_or_exit("TINGWU_APP_KEY")
    return TingwuClient(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        app_key=app_key,
    )


@app.command()
def create_task(
    file_url: Optional[str] = typer.Option(
        None, "--url", "-u", help="音视频文件的URL地址"
    ),
    language: str = typer.Option(
        "cn", "--language", "-l", help="源语言，默认为中文(cn)"
    ),
    speakers: Optional[int] = typer.Option(  # 修改为 Optional，且限制值为 0 或 2
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
    """
    创建听悟离线转写任务
    """
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


@app.command()
def get_status(
    task_id: str = typer.Option(..., "--task-id", "-t", help="要查询的任务ID")
) -> None:
    """查询任务状态"""
    try:
        client = create_client()

        with console.status("[bold green]正在查询任务状态...") as status:
            response = client.get_task_status(task_id)

        # 打印响应
        print_response(response)

    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        sys.exit(1)


@app.command()
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
            result = client.wait_for_task_completion(
                task_id=task_id,
                timeout=wait_time,
                interval=interval,
                output_dir=output_dir,
            )

        console.print("[bold green]任务完成！[/bold green]")
        print_response(result)

        # 自动下载结果文件
        if "Data" in result and "Result" in result["Data"]:
            console.print("\n[bold green]开始下载结果文件...[/bold green]")
            download_results(result["Data"]["Result"], output_dir)

        # 自动格式化转写结果
        if "Transcription" in result:
            console.print("\n[bold green]开始格式化转写结果...[/bold green]")
            format_transcription(result, task_id, output_dir)

    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")
        sys.exit(1)


@app.command()
def version():
    """显示版本信息"""
    console.print("听悟客户端 v0.1.0")


def main():
    """主函数"""
    try:
        app()
    except Exception as e:
        console.print(f"[red]程序错误: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
