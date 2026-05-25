from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class LangChainChatService:
    def __init__(self) -> None:
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "너는 {tone} 설명하는 백엔드/LLM 멘토야. "
                    "답변은 한국어로 하고, 핵심을 먼저 말해.",
                ),
                ("human", "{message}"),
            ]
        )

        self.model = FakeListChatModel(
            responses=[
                "첫 번째 LangChain mock 응답입니다.",
                "두 번째 LangChain mock 응답입니다.",
                "세 번째 LangChain mock 응답입니다.",
            ]
        )

        self.parser = StrOutputParser()

        self.chain = self.prompt | self.model | self.parser

    async def chat(self, message: str, tone: str) -> str:
        return await self.chain.ainvoke(
            {
                "message": message,
                "tone": tone,
            }
        )


langchain_chat_service = LangChainChatService()