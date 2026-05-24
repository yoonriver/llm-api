import asyncio

import boto3

from app.core.config import settings


class S3StorageService:
    def __init__(self) -> None:
        if not settings.s3_bucket:
            raise RuntimeError("S3_BUCKET is not set")

        self.bucket = settings.s3_bucket
        self.client = boto3.client(
            "s3",
            region_name=settings.aws_region,
        )

    async def put_text(self, object_key: str, content: str) -> None:
        await asyncio.to_thread(
            self._put_text_sync,
            object_key,
            content,
        )

    def _put_text_sync(self, object_key: str, content: str) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=object_key,
            Body=content.encode("utf-8"),
            ContentType="text/plain; charset=utf-8",
        )

    async def get_text(self, object_key: str) -> str:
        return await asyncio.to_thread(
            self._get_text_sync,
            object_key,
        )

    def _get_text_sync(self, object_key: str) -> str:
        response = self.client.get_object(
            Bucket=self.bucket,
            Key=object_key,
        )

        return response["Body"].read().decode("utf-8")


s3_storage_service = S3StorageService()