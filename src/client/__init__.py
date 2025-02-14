from .base import BaseClient
from .task import TaskMixin
from .result import ResultMixin


class TingwuClient(BaseClient, TaskMixin, ResultMixin):
    """听悟API客户端"""

    pass
