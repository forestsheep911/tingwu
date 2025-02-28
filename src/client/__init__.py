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
    from rich.console import Console
    from src.utils import load_env_or_exit
    
    console = Console()
    
    # 获取必要的环境变量（每次获取都会重新加载）
    access_key_id = load_env_or_exit("ALIBABA_CLOUD_ACCESS_KEY_ID")
    access_key_secret = load_env_or_exit("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    app_key = load_env_or_exit("TINGWU_APP_KEY")
    
    return TingwuClient(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        app_key=app_key,
    )

__all__ = ["TingwuClient", "create_client"]
