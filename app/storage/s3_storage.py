from typing import Optional
import boto3
from botocore.exceptions import ClientError
from app.storage.base import BaseStorage
from app.core.config import get_settings

settings = get_settings()


class S3Storage(BaseStorage):
    """S3-compatible storage driver for MinIO / AWS S3 deployment."""
    def __init__(self):
        self.bucket = settings.S3_BUCKET_NAME
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION,
        )

    async def save(self, file_data: bytes, filename: str, subfolder: str = "") -> str:
        key = f"{subfolder}/{filename}".lstrip("/")
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_data
        )
        return key

    async def read(self, path_or_key: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.bucket, Key=path_or_key)
        return response["Body"].read()

    async def delete(self, path_or_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=path_or_key)
            return True
        except ClientError:
            return False

    async def exists(self, path_or_key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=path_or_key)
            return True
        except ClientError:
            return False


def get_storage() -> BaseStorage:
    if settings.STORAGE_BACKEND.lower() == "s3":
        return S3Storage()
    return LocalStorage()
