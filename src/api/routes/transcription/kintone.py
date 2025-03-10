"""Kintone 文件下载逻辑"""

import requests
import os
from typing import Dict, Any

KINTONE_API_URL = "https://2water.cybozu.com/k/v1"
KINTONE_API_TOKEN = os.environ["KINTONE_API_TOKEN"]
KINTONE_APP_ID = "8"


def test_network_connectivity():
    """测试网络连通性"""
    test_urls = [
        "https://www.bing.com",  # 测试公网访问
        "https://movie.douban.com/",  # 测试公网访问
        "https://2water.cybozu.com",  # 测试 Kintone 域名
    ]
    for url in test_urls:
        try:
            print(f"Testing connectivity to {url}...", flush=True)
            response = requests.get(url, timeout=10)
            print(f"Response from {url}: {response.status_code}", flush=True)
        except requests.exceptions.Timeout:
            print(f"Failed to connect to {url}: Timeout after 10 seconds", flush=True)
        except requests.exceptions.ConnectionError as e:
            print(
                f"Failed to connect to {url}: Connection error - {str(e)}", flush=True
            )
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to {url}: {str(e)}", flush=True)


def get_kintone_file(record_id: str) -> str:
    """从 Kintone 下载文件"""
    headers = {"X-Cybozu-API-Token": KINTONE_API_TOKEN}

    # 测试网络连通性
    print("Performing network connectivity test before Kintone request...", flush=True)
    test_network_connectivity()

    # 请求记录
    url = f"{KINTONE_API_URL}/record.json?app={KINTONE_APP_ID}&id={record_id}"
    print(f"Requesting Kintone API: {url}", flush=True)
    print(f"Using API token: {KINTONE_API_TOKEN[:5]}... (masked)", flush=True)
    print(f"Request headers: {headers}", flush=True)

    try:
        print("Sending Kintone record request...", flush=True)
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Kintone response status: {response.status_code}", flush=True)
        print(f"Kintone response content: {response.text}", flush=True)
        response.raise_for_status()
        record = response.json()["record"]
        attachment = record.get("audio_file", {}).get("value", [])
        if not attachment:
            raise ValueError("记录中没有附件")

        # 下载文件
        file_key = attachment[0]["fileKey"]
        file_name = attachment[0]["name"]
        download_url = f"{KINTONE_API_URL}/file.json?fileKey={file_key}"
        print(f"Downloading file from: {download_url}", flush=True)

        print("Sending Kintone file download request...", flush=True)
        file_response = requests.get(download_url, headers=headers, timeout=30)
        print(f"File download status: {file_response.status_code}", flush=True)
        file_response.raise_for_status()

        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        local_path = os.path.join(temp_dir, file_name)
        with open(local_path, "wb") as f:
            f.write(file_response.content)
        print(f"Downloaded Kintone file to {local_path}", flush=True)
        return local_path

    except requests.exceptions.Timeout:
        print("Kintone request timed out after 30 seconds", flush=True)
        raise
    except requests.exceptions.ConnectionError as e:
        print(f"Kintone connection error: {str(e)}", flush=True)
        raise
    except requests.exceptions.RequestException as e:
        print(f"Kintone request failed: {str(e)}", flush=True)
        raise
    except Exception as e:
        print(f"Unexpected error in Kintone file download: {str(e)}", flush=True)
        raise
