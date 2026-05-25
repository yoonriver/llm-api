from pydantic import BaseModel, Field


class ChainChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    tone: str = Field(default="친절하게", description="Answer tone")


class ChainChatResponse(BaseModel):
    answer: str
    chain_type: str