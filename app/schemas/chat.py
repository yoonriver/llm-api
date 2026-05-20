from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    system_prompt: str | None = Field(
        default=None,
        description="Optional system prompt",
    )

class ChatResponse(BaseModel):
    answer: str
    model: str