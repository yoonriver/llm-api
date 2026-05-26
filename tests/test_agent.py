from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_chat_llm_framework_question():
    response = client.post(
        "/agent/chat",
        json={
            "message": "LangGraph는 LangChain이랑 뭐가 달라?",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["question_type"] == "llm_framework"
    assert data["validated"] is True
    assert "classify_question:llm_framework" in data["trace"]
    assert "generate_answer" in data["trace"]


def test_agent_chat_aws_question():
    response = client.post(
        "/agent/chat",
        json={
            "message": "ECS에서 task role이 왜 필요해?",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["question_type"] == "aws"
    assert data["validated"] is True


def test_agent_chat_requires_message():
    response = client.post(
        "/agent/chat",
        json={},
    )

    assert response.status_code == 422