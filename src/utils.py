# src/utils.py
import os
import json
from pathlib import Path
from typing import Dict, Any
from rich.table import Table
from rich.console import Console
from dotenv import load_dotenv

console = Console()


def load_env_or_exit(env_name: str) -> str:
    root_dir = Path(__file__).parent.parent
    env_path = root_dir / ".env"
    if not load_dotenv(env_path, override=True):
        console.print(f"[yellow]警告: 无法加载环境变量文件: {env_path}[/yellow]")
    value = os.getenv(env_name)
    console.print(f"[blue]加载的环境变量 {env_name}: {value}[/blue]")  # 添加调试输出
    if not value:
        console.print(f"[red]错误: 环境变量 {env_name} 未设置[/red]")
        exit(1)
    return value


def print_response(response: Dict[str, Any]) -> None:
    """美化输出API响应"""
    if not response:
        console.print("[yellow]警告: 收到空响应[/yellow]")
        return

    # 创建表格
    table = Table(show_header=True)
    table.add_column("字段", style="cyan")
    table.add_column("值", style="green")

    # 添加基本信息
    if "Code" in response:
        table.add_row("状态码", str(response["Code"]))
    if "Message" in response:
        table.add_row("消息", response["Message"])
    if "RequestId" in response:
        table.add_row("请求ID", response["RequestId"])

    # 添加任务信息
    if "Data" in response and isinstance(response["Data"], dict):
        data = response["Data"]
        for key, value in data.items():
            table.add_row(key, str(value))

    console.print("\n[bold]API响应详情:[/bold]")
    console.print(table)

    # 保存响应到文件
    save_response(response)


def save_response(response: Dict[str, Any]) -> None:
    """保存响应到文件"""
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # 使用请求ID或时间戳作为文件名
        filename = response.get("RequestId", "response") + ".json"
        output_path = output_dir / filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)

        console.print(f"\n[green]响应已保存到: {output_path}[/green]")
    except Exception as e:
        console.print(f"[yellow]警告: 保存响应失败: {e}[/yellow]")
