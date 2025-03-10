#!/bin/bash
if [ -f .env ]; then
    export $(grep -v '^#' .env | grep -v '^$' | xargs)
else
    echo "Error: .env file not found!"
    exit 1
fi

# 停止并删除旧容器
docker stop tingwu-container 2>/dev/null || true
docker rm tingwu-container 2>/dev/null || true

# 检查并构建镜像
if ! docker images -q tingwuimage:latest | grep -q .; then
    echo "Building tingwuimage:latest..."
    docker build -t tingwuimage:latest . || {
        echo "Error: Failed to build tingwuimage:latest"
        exit 1
    }
else
    echo "Using existing tingwuimage:latest..."
fi

# 运行容器
docker run -d --name tingwu-container -p 9000:9000 \
  -v /mnt/d/usr/bxu/dev/mypj/tingwu:/code \
  -e TINGWU_ACCESS_KEY_ID="$TINGWU_ACCESS_KEY_ID" \
  -e TINGWU_ACCESS_KEY_SECRET="$TINGWU_ACCESS_KEY_SECRET" \
  -e TINGWU_APP_KEY="$TINGWU_APP_KEY" \
  -e OSS_ACCESS_KEY_ID="$OSS_ACCESS_KEY_ID" \
  -e OSS_ACCESS_KEY_SECRET="$OSS_ACCESS_KEY_SECRET" \
  -e OSS_ENDPOINT="$OSS_ENDPOINT" \
  -e OSS_BUCKET_NAME="$OSS_BUCKET_NAME" \
  -e KINTONE_API_TOKEN="$KINTONE_API_TOKEN" \
  tingwuimage:latest \
  uvicorn src.api:app --host 0.0.0.0 --port 9000 --reload --reload-dir /code --log-level debug