from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    message: str
    question_type: str
    answer: str
    validated: bool
    trace: list[str]


def classify_question(state: AgentState) -> dict:
    message = state["message"]

    if "AWS" in message or "ECS" in message or "Bedrock" in message or "S3" in message:
        question_type = "aws"
    elif "LangGraph" in message or "LangChain" in message:
        question_type = "llm_framework"
    else:
        question_type = "general"

    return {
        "question_type": question_type,
        "trace": state["trace"] + [f"classify_question:{question_type}"],
    }


def generate_answer(state: AgentState) -> dict:
    question_type = state["question_type"]
    message = state["message"]

    if question_type == "aws":
        answer = (
            "AWS 관련 질문으로 분류했습니다. "
            "이 질문은 클라우드 인프라, 배포, 권한, 저장소 같은 주제와 관련이 있습니다. "
            f"질문: {message}"
        )
    elif question_type == "llm_framework":
        answer = (
            "LangChain/LangGraph 관련 질문으로 분류했습니다. "
            "LangChain은 LLM 호출 구성 요소를 조합하는 데 가깝고, "
            "LangGraph는 상태 기반 workflow를 구성하는 데 가깝습니다. "
            f"질문: {message}"
        )
    else:
        answer = (
            "일반 질문으로 분류했습니다. "
            "현재 예제에서는 mock 답변을 반환합니다. "
            f"질문: {message}"
        )

    return {
        "answer": answer,
        "trace": state["trace"] + ["generate_answer"],
    }


def validate_answer(state: AgentState) -> dict:
    answer = state["answer"]

    validated = bool(answer and len(answer.strip()) > 0)

    return {
        "validated": validated,
        "trace": state["trace"] + [f"validate_answer:{validated}"],
    }


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_question", classify_question)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("validate_answer", validate_answer)

    graph.add_edge(START, "classify_question")
    graph.add_edge("classify_question", "generate_answer")
    graph.add_edge("generate_answer", "validate_answer")
    graph.add_edge("validate_answer", END)

    return graph.compile()


agent_graph = build_agent_graph()


class AgentGraphService:
    async def chat(self, message: str) -> AgentState:
        initial_state: AgentState = {
            "message": message,
            "question_type": "",
            "answer": "",
            "validated": False,
            "trace": [],
        }

        result = await agent_graph.ainvoke(initial_state)

        return result


agent_graph_service = AgentGraphService()