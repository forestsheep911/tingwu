# 听悟 API 服务

这是一个基于阿里云听悟服务的 API 封装和命令行工具，提供音视频文件的转写、翻译等功能。通过 FastAPI 提供 RESTful API 接口，适用于开发者快速集成音视频处理能力。

## 功能特性

- **音视频文件转写**：支持多语言转写和说话人分离。
- **多语言翻译**：将转写结果翻译为指定语言（如英语）。
- **说话人分离**：识别并区分多个说话人。
- **章节速览**：自动生成音频章节划分。
- **会议智能**：提取会议中的关键信息和行动项。
- **内容摘要**：生成音频内容的简要摘要。
- **PPT 提取**：从音频中提取相关幻灯片内容。
- **口语书面化**：将口语化的转写结果优化为书面语言。

## 环境要求

- **Python**：>= 3.11
- **Poetry**：包管理工具（推荐版本 >= 2.0.0）
- **阿里云账号**：需开通听悟服务并获取 Access Key 和 App Key
- **操作系统**：Windows、Linux 或 macOS

## 安装

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/tingwu.git
cd tingwu
```

### 2. 安装依赖
使用 Poetry 安装项目依赖：
```bash
poetry install
```

### 3. 配置环境变量
复制 `.env.example` 文件到 `.env` 文件：
```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：
```bash
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
TINGWU_APP_KEY=your_app_key
AUDIO_FILE_URL=your_default_audio_file_url  # 可选，默认的音频文件URL
```

### 4. SSL 证书配置
开发环境下生成自签名证书：
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

## 使用方法

### 1. 启动 API 服务
在项目根目录下运行：
```bash
poetry run python -m src.main
```

- 默认运行在 https://localhost:8000
- 使用 SSL 加密（使用自签名证书）
- 开发模式下启用热重载

### 2. API 使用示例

#### PowerShell 示例

创建转写任务：
```powershell
$body = @{
    language = "cn"
    speakers = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://localhost:8000/api/v1/transcribe" `
    -Method Post `
    -Body $body `
    -ContentType "application/json" `
    -SkipCertificateCheck
```

查询任务状态：
```powershell
Invoke-RestMethod -Uri "https://localhost:8000/api/v1/task/{task_id}" `
    -Method Get `
    -SkipCertificateCheck
```

获取任务结果：
```powershell
Invoke-RestMethod -Uri "https://localhost:8000/api/v1/task/{task_id}/result?output_dir=output" `
    -Method Get `
    -SkipCertificateCheck
```

#### curl 示例（Windows CMD）
创建转写任务：
```bash
curl -k -X POST "https://localhost:8000/api/v1/transcribe" ^
     -H "Content-Type: application/json" ^
     -d "{\"language\": \"cn\", \"speakers\": 0}"
```

查询任务状态：
```bash
curl -k "https://localhost:8000/api/v1/task/{task_id}"
```

获取任务结果：
```bash
curl -k "https://localhost:8000/api/v1/task/{task_id}/result?output_dir=output"
```

## 项目结构
```
tingwu/
├── .env.example      # 环境变量模板
├── .gitignore        # Git 忽略规则
├── cert.pem          # SSL证书
├── key.pem           # SSL私钥
├── pyproject.toml    # Poetry 配置文件
├── README.md         # 项目说明
└── src/              # 源代码
    ├── main.py       # API 服务入口
    ├── api/          # API 路由和模型
    │   ├── __init__.py
    │   ├── models.py
    │   └── routes/
    ├── client/       # 阿里云听悟客户端
    ├── processors/   # 结果处理器
    └── utils/        # 工具函数
```
