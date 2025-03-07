# src/main.py
"""主程序入口"""
import sys
from pathlib import Path
import uvicorn
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件中的环境变量

# 添加项目根目录到Python路径
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

def main():
    """启动服务器"""
    uvicorn.run(
        "src.api:app",  # 使用导入字符串而不是实例
        host="localhost",
        port=8000,
        reload=True,  # 开发模式启用热重载
        ssl_keyfile="key.pem",  # SSL证书文件
        ssl_certfile="cert.pem"
    )

if __name__ == "__main__":
    main()
