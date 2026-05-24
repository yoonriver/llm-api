import asyncio
from typing import Protocol

import boto3

from app.core.config import settings


class LLMService(Protocol):
    async def chat(self, message: str, system_prompt: str | None = None) -> str:
        ...


class MockLLMService:
    async def chat(self, message: str, system_prompt: str | None = None) -> str:
        await asyncio.sleep(0.1)

        if system_prompt:
            return f"[mock] system_prompt='{system_prompt}' 조건에서 '{message}'에 대한 답변입니다."

        return f"[mock] {message}에 대한 답변입니다."


class BedrockClaudeService:
    def __init__(self) -> None:
        if not settings.bedrock_model_id:
            raise RuntimeError("BEDROCK_MODEL_ID is not set")

        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
        )
        self.model_id = settings.bedrock_model_id

    async def chat(self, message: str, system_prompt: str | None = None) -> str:
        return await asyncio.to_thread(
            self._chat_sync,
            message,
            system_prompt,
        )

    def _chat_sync(self, message: str, system_prompt: str | None = None) -> str:
        request = {
            "modelId": self.model_id,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": message,
                        }
                    ],
                }
            ],
            "inferenceConfig": {
                "maxTokens": 500,
                "temperature": 0.7,
            },
        }

        if system_prompt:
            request["system"] = [
                {
                    "text": system_prompt,
                }
            ]

        response = self.client.converse(**request)

        return response["output"]["message"]["content"][0]["text"]


def create_llm_service() -> LLMService:
    if settings.use_bedrock:
        return BedrockClaudeService()

    return MockLLMService()


llm_service = create_llm_service()