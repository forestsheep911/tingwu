# src/main.py
import sys
from pathlib import Path

# 添加项目根目录到Python路径
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import typer
from rich.console import Console
from src.commands import process, version, wait_task

app = typer.Typer()
console = Console()

# 注册命令
app.command()(process)
app.command()(version)
app.command()(wait_task)

def main():
    """主函数"""
    try:
        app()
    except Exception as e:
        console.print(f"[red]程序错误: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
