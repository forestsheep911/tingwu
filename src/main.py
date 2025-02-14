# src/main.py
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from dotenv import load_dotenv

from client import TingwuClient
from utils import load_env_or_exit, print_response

app = typer.Typer()
console = Console()


def create_client() -> TingwuClient:
    """创建并返回TingwuClient实例"""
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / ".env"

    # 显式指定.env文件路径
    if not load_dotenv(env_path):
        console.print(f"[yellow]警告: 无法加载环境变量文件: {env_path}[/yellow]")

    # 打印当前工作目录和env文件位置（调试用）
    console.print(f"[blue]当前工作目录: {Path.cwd()}[/blue]")
    console.print(f"[blue]env文件路径: {env_path}[/blue]")
    console.print(f"[blue]env文件是否存在: {env_path.exists()}[/blue]")

    # 获取必要的环境变量
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
    ),  # 改为None表示可选
    language: str = typer.Option(
        "cn", "--language", "-l", help="源语言，默认为中文(cn)"
    ),
    speakers: int = typer.Option(
        0, "--speakers", "-s", help="说话人数量，0表示自动检测"
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
        if speakers > 0:
            console.print(f"说话人数: {speakers}")

        # 创建任务
        with console.status("[bold green]正在创建转写任务...") as status:
            response = client.create_offline_task(
                file_url=file_url,
                source_language=language,
                enable_diarization=speakers > 0,
                speaker_count=speakers,
                enable_translation=translate,
                target_languages=[target_lang] if translate else None,
                enable_chapters=chapters,
                enable_meeting_assistance=meeting,
                enable_summarization=summary,
                enable_ppt=ppt,
                enable_text_polish=polish,
            )

        # 打印响应
        print_response(response)

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
    """等待任务完成并获取结果"""
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
