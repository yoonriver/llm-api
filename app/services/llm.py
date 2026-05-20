import asyncio

from app.core.config import settings


class MockLLMService:
    async def chat(self, message: str, system_prompt: str | None = None) -> str:
        """
        지금은 Bedrock Claude를 호출하지 않고 mock 답변만 반환한다.
        나중에 이 클래스를 BedrockClaudeService로 교체할 것이다.
        """

        await asyncio.sleep(0.1)

        if system_prompt:
            return f"[mock] system_prompt='{system_prompt}' 조건에서 '{message}'에 대한 답변입니다."

        return f"[mock] {message}에 대한 답변입니다."


llm_service = MockLLMService()