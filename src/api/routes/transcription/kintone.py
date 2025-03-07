"""Kintone 文件下载逻辑"""

import requests
import os
from typing import Dict, Any

KINTONE_API_URL = "https://2water.cybozu.com/k/v1"
KINTONE_API_TOKEN = os.environ["KINTONE_API_TOKEN"]
KINTONE_APP_ID = "8"


def get_kintone_file(record_id: str) -> str:
    headers = {"X-Cybozu-API-Token": KINTONE_API_TOKEN}
    url = f"{KINTONE_API_URL}/record.json?app={KINTONE_APP_ID}&id={record_id}"
    print(f"Requesting Kintone API: {url}", flush=True)
    response = requests.get(url, headers=headers)
    print(f"Kintone response status: {response.status_code}", flush=True)
    print(f"Kintone response content: {response.text}", flush=True)
    response.raise_for_status()
    record = response.json()["record"]
    attachment = record.get("audio_file", {}).get("value", [])
    if not attachment:
        raise ValueError("记录中没有附件")
    file_key = attachment[0]["fileKey"]
    file_name = attachment[0]["name"]
    download_url = f"{KINTONE_API_URL}/file.json?fileKey={file_key}"
    print(f"Downloading file from: {download_url}", flush=True)
    file_response = requests.get(download_url, headers=headers)
    print(f"File download status: {file_response.status_code}", flush=True)
    file_response.raise_for_status()
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    local_path = os.path.join(temp_dir, file_name)
    with open(local_path, "wb") as f:
        f.write(file_response.content)
    print(f"Downloaded Kintone file to {local_path}", flush=True)
    return local_path
