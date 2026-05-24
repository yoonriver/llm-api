from fastapi import APIRouter

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm import llm_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer = await llm_service.chat(
        message=request.message,
        system_prompt=request.system_prompt,
    )

    model_name = (
        settings.bedrock_model_id
        if settings.use_bedrock and settings.bedrock_model_id
        else settings.mock_model_name
    )

    return ChatResponse(
        answer=answer,
        model=model_name,
    )