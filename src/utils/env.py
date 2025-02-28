"""环境变量相关工具"""
import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, find_dotenv, dotenv_values
from rich.console import Console

console = Console()

def reload_env() -> None:
    """强制重新加载环境变量"""
    # 清除所有已加载的环境变量
    dotenv_path = find_dotenv()
    if dotenv_path:
        for key in dotenv_values(dotenv_path).keys():
            if key in os.environ:
                del os.environ[key]
    
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent.parent
    env_path = root_dir / ".env"
    
    # 强制重新加载
    if not load_dotenv(env_path, override=True):
        console.print(f"[yellow]警告: 无法加载环境变量文件: {env_path}[/yellow]")

def load_env_or_exit(key: str) -> str:
    """获取环境变量，如果不存在则退出程序"""
    # 每次获取前都重新加载
    reload_env()
    
    value = os.getenv(key)
    if not value:
        console.print(f"[red]错误: 环境变量 {key} 未设置[/red]")
        sys.exit(1)
    return value 