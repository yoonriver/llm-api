from fastapi import APIRouter

from app.schemas.agent import AgentChatRequest, AgentChatResponse
from app.services.agent_graph import agent_graph_service

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(request: AgentChatRequest) -> AgentChatResponse:
    result = await agent_graph_service.chat(request.message)

    return AgentChatResponse(
        question_type=result["question_type"],
        answer=result["answer"],
        validated=result["validated"],
        trace=result["trace"],
    )