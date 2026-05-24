from fastapi import APIRouter

from app.schemas.history import (
    ChatHistoryItem,
    ChatHistoryListResponse,
    ChatHistoryPutRequest,
    ChatHistoryPutResponse,
)
from app.services.history import chat_history_service

router = APIRouter(prefix="/history", tags=["history"])


@router.post("", response_model=ChatHistoryPutResponse)
async def put_history(request: ChatHistoryPutRequest) -> ChatHistoryPutResponse:
    item = await chat_history_service.put_history(
        session_id=request.session_id,
        message=request.message,
        answer=request.answer,
    )

    return ChatHistoryPutResponse(
        item=ChatHistoryItem(**item),
    )


@router.get("/{session_id}", response_model=ChatHistoryListResponse)
async def list_history(session_id: str) -> ChatHistoryListResponse:
    items = await chat_history_service.list_history(session_id)

    return ChatHistoryListResponse(
        session_id=session_id,
        items=[ChatHistoryItem(**item) for item in items],
    )