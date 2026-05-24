from pydantic import BaseModel, Field


class S3TextPutRequest(BaseModel):
    object_key: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class S3TextPutResponse(BaseModel):
    bucket: str
    object_key: str
    status: str


class S3TextGetResponse(BaseModel):
    bucket: str
    object_key: str
    content: str