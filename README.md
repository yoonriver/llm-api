# Bedrock Claude FastAPI Server

## Day 1

오늘 구현한 것:

- FastAPI 프로젝트 구조 생성
- GET /health API 구현
- POST /chat mock API 구현
- Pydantic request/response schema 작성
- MockLLMService 작성
- pytest 기본 테스트 작성

## Run

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

## API Test

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

```powershell
$body = @{
    message = "안녕하세요"
    system_prompt = "친절하게 답변하세요"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Test

```powershell
pytest
```