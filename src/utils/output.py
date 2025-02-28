"""输出格式化工具"""
from typing import Dict, Any
from rich.console import Console

console = Console()

def print_response(response: Dict[str, Any]) -> None:
    """格式化打印API响应"""
    if "RequestId" in response:
        console.print(f"\n[dim]RequestId: {response['RequestId']}[/dim]")
    if "Message" in response:
        console.print(f"[bold]Message: {response['Message']}[/bold]")
    if "Data" in response:
        console.print("\n[bold]Data:[/bold]")
        for key, value in response["Data"].items():
            console.print(f"{key}: {value}")

def format_time(ms: int) -> str:
    """将毫秒转换为 [mm:ss] 格式"""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"[{minutes:02d}:{seconds:02d}]" 