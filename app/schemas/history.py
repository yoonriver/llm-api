from pydantic import BaseModel, Field


class ChatHistoryPutRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)


class ChatHistoryItem(BaseModel):
    session_id: str
    created_at: str
    chat_id: str
    message: str
    answer: str


class ChatHistoryPutResponse(BaseModel):
    item: ChatHistoryItem


class ChatHistoryListResponse(BaseModel):
    session_id: str
    items: list[ChatHistoryItem]