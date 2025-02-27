"""听悟API客户端"""
from .base import BaseClient
from .task import TaskMixin
from .result import ResultMixin


class TingwuClient(BaseClient, TaskMixin, ResultMixin):
    """听悟API客户端"""
    pass


# 在TingwuClient定义之后，再导入和定义create_client
def create_client() -> TingwuClient:
    """创建并返回TingwuClient实例"""
    from pathlib import Path
    from dotenv import load_dotenv
    from rich.console import Console
    from src.utils import load_env_or_exit
    
    console = Console()
    
    root_dir = Path(__file__).parent.parent.parent
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

__all__ = ["TingwuClient", "create_client"]
