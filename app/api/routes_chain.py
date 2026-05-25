from fastapi import APIRouter

from app.schemas.chain import ChainChatRequest, ChainChatResponse
from app.services.chain import langchain_chat_service

router = APIRouter(prefix="/chain", tags=["chain"])


@router.post("/chat", response_model=ChainChatResponse)
async def chain_chat(request: ChainChatRequest) -> ChainChatResponse:
    answer = await langchain_chat_service.chat(
        message=request.message,
        tone=request.tone,
    )

    return ChainChatResponse(
        answer=answer,
        chain_type="langchain-fake-chat",
    )