from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.auth.credentials import AccessKeyCredential
from typing import Dict, Any


class BaseClient:
    """听悟API基础客户端"""

    def __init__(self, access_key_id: str, access_key_secret: str, app_key: str):
        """初始化客户端

        Args:
            access_key_id: 阿里云访问密钥ID
            access_key_secret: 阿里云访问密钥密码
            app_key: 听悟应用的AppKey
        """
        self.app_key = app_key
        credentials = AccessKeyCredential(access_key_id, access_key_secret)
        self.client = AcsClient(region_id="cn-beijing", credential=credentials)

    def _create_request(self, uri: str, method: str = "PUT") -> CommonRequest:
        """创建通用请求对象"""
        request = CommonRequest()
        request.set_accept_format("json")
        request.set_domain("tingwu.cn-beijing.aliyuncs.com")
        request.set_version("2023-09-30")
        request.set_protocol_type("https")
        request.set_method(method)
        request.set_uri_pattern(uri)
        request.add_header("Content-Type", "application/json")
        return request
