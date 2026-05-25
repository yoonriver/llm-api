from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chain_chat_success():
    response = client.post(
        "/chain/chat",
        json={
            "message": "LangChain이 뭐야?",
            "tone": "친절하게",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "answer" in data
    assert data["chain_type"] == "langchain-fake-chat"


def test_chain_chat_requires_message():
    response = client.post(
        "/chain/chat",
        json={
            "tone": "친절하게",
        },
    )

    assert response.status_code == 422