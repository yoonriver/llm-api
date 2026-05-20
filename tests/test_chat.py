from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_success():
    response = client.post(
        "/chat",
        json={
            "message": "안녕하세요",
            "system_prompt": "친절하게 답변하세요",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "answer" in data
    assert data["model"] == "mock-claude"


def test_chat_requires_message():
    response = client.post(
        "/chat",
        json={
            "system_prompt": "친절하게 답변하세요",
        },
    )

    assert response.status_code == 422