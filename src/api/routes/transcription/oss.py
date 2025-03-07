"""OSS 上传和签名 URL 生成"""

import os
import oss2


def upload_to_oss(local_file_path: str, bucket_name: str, object_name: str) -> str:
    """上传文件到 OSS 并返回无签名 URL

    Args:
        local_file_path: 本地文件路径
        bucket_name: OSS Bucket 名称
        object_name: OSS 对象名称

    Returns:
        str: OSS 文件的无签名 URL
    """
    auth = oss2.Auth(
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
    )
    bucket = oss2.Bucket(auth, os.getenv("OSS_ENDPOINT"), bucket_name)

    with open(local_file_path, "rb") as fileobj:
        bucket.put_object(object_name, fileobj)

    oss_url = f"https://{bucket_name}.{os.getenv('OSS_ENDPOINT')}/{object_name}"
    print(f"Uploaded to OSS: {oss_url}", flush=True)
    return oss_url


def generate_signed_url(bucket_name: str, object_name: str, expires: int = 3600) -> str:
    """生成 OSS 文件的签名 URL

    Args:
        bucket_name: OSS Bucket 名称
        object_name: OSS 对象名称
        expires: 签名有效期（秒），默认 1 小时

    Returns:
        str: 签名 URL
    """
    auth = oss2.Auth(
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"),
        os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"),
    )
    bucket = oss2.Bucket(auth, os.getenv("OSS_ENDPOINT"), bucket_name)
    signed_url = bucket.sign_url("GET", object_name, expires)
    print(f"Generated signed URL: {signed_url}", flush=True)
    return signed_url
