from fastapi import APIRouter

from app.core.config import settings
from app.schemas.storage import (
    S3TextGetResponse,
    S3TextPutRequest,
    S3TextPutResponse,
)
from app.services.storage import s3_storage_service

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/s3/text", response_model=S3TextPutResponse)
async def put_s3_text(request: S3TextPutRequest) -> S3TextPutResponse:
    await s3_storage_service.put_text(
        object_key=request.object_key,
        content=request.content,
    )

    return S3TextPutResponse(
        bucket=settings.s3_bucket or "",
        object_key=request.object_key,
        status="saved",
    )


@router.get("/s3/text/{object_key:path}", response_model=S3TextGetResponse)
async def get_s3_text(object_key: str) -> S3TextGetResponse:
    content = await s3_storage_service.get_text(object_key)

    return S3TextGetResponse(
        bucket=settings.s3_bucket or "",
        object_key=object_key,
        content=content,
    )