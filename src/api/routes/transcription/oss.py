import os
import oss2
from rich.console import Console

console = Console()


def upload_to_oss(local_file_path: str, bucket_name: str, object_name: str) -> str:
    access_key_id = os.getenv("OSS_ACCESS_KEY_ID")
    access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
    endpoint = os.getenv("OSS_ENDPOINT")
    if not all([access_key_id, access_key_secret, endpoint]):
        missing = [
            k
            for k, v in {
                "OSS_ACCESS_KEY_ID": access_key_id,
                "OSS_ACCESS_KEY_SECRET": access_key_secret,
                "OSS_ENDPOINT": endpoint,
            }.items()
            if not v
        ]
        raise ValueError(f"缺少环境变量: {', '.join(missing)}")
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    with open(local_file_path, "rb") as fileobj:
        bucket.put_object(object_name, fileobj)
    oss_url = f"https://{bucket_name}.{endpoint}/{object_name}"
    console.print(f"Uploaded to OSS: {oss_url}")  # 移除 flush=True
    return oss_url


def generate_signed_url(bucket_name: str, object_name: str, expires: int = 3600) -> str:
    access_key_id = os.getenv("OSS_ACCESS_KEY_ID")
    access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
    endpoint = os.getenv("OSS_ENDPOINT")
    if not all([access_key_id, access_key_secret, endpoint]):
        missing = [
            k
            for k, v in {
                "OSS_ACCESS_KEY_ID": access_key_id,
                "OSS_ACCESS_KEY_SECRET": access_key_secret,
                "OSS_ENDPOINT": endpoint,
            }.items()
            if not v
        ]
        raise ValueError(f"缺少环境变量: {', '.join(missing)}")
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)
    signed_url = bucket.sign_url("GET", object_name, expires)
    console.print(f"Generated signed URL: {signed_url}")  # 移除 flush=True
    return signed_url
