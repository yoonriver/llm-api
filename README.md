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
---------------------------------------------------------------------------------

## Day 2 - Docker

### 목표

FastAPI 앱을 Docker 컨테이너 안에서 실행한다.

오늘의 목표 흐름:

```text
FastAPI 코드
  ↓
Dockerfile
  ↓
Docker image
  ↓
Docker container
  ↓
/health, /chat 테스트
```

---

### 오늘 한 일

- `requirements.txt` 생성
- `Dockerfile` 생성
- `.dockerignore` 생성
- Docker image build
- Docker container 실행
- `GET /health` 테스트
- `POST /chat` 테스트
- `message` 누락 시 422 검증 에러 확인
- `docker logs`로 컨테이너 로그 확인
- Docker image tag 연습

---

### Docker image build

```powershell
docker build -t llm-api:local .
```

성공하면 아래 명령어로 image를 확인할 수 있다.

```powershell
docker images
```

예상 결과:

```text
REPOSITORY   TAG     IMAGE ID
llm-api      local   ...
```

---

### Docker container 실행

```powershell
docker run --rm --name llm-api-local -p 8000:8000 --env-file .env llm-api:local
```

옵션 의미:

```text
--rm
  컨테이너 종료 시 자동 삭제

--name llm-api-local
  컨테이너 이름 지정

-p 8000:8000
  내 PC의 8000번 포트를 컨테이너 내부 8000번 포트와 연결

--env-file .env
  .env 파일의 환경변수를 컨테이너에 주입

llm-api:local
  실행할 Docker image
```

---

### 백그라운드 실행

터미널을 점유하지 않고 백그라운드에서 실행하려면 `-d` 옵션을 사용한다.

```powershell
docker run -d --rm --name llm-api-local -p 8000:8000 --env-file .env llm-api:local
```

실행 중인 컨테이너 확인:

```powershell
docker ps
```

컨테이너 종료:

```powershell
docker stop llm-api-local
```

---

### `/health` 테스트

```powershell
curl.exe http://127.0.0.1:8000/health
```

예상 응답:

```json
{
  "status": "ok"
}
```

---

### `/chat` 테스트

PowerShell에서 한글 JSON이 깨질 수 있으므로, JSON 파일을 만들어서 요청한다.

프로젝트 루트에 `request-chat.json` 파일을 만든다.

```json
{
  "message": "Docker에서 실행 중이야?",
  "system_prompt": "짧게 답해줘"
}
```

요청:

```powershell
curl.exe -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" --data-binary "@request-chat.json"
```

예상 응답:

```json
{
  "answer": "[mock] system_prompt='짧게 답해줘' 조건에서 'Docker에서 실행 중이야?'에 대한 답변입니다.",
  "model": "mock-claude"
}
```

---

### 검증 에러 테스트

`message`가 없는 요청을 보내서 FastAPI/Pydantic 검증이 정상 동작하는지 확인한다.

프로젝트 루트에 `request-bad.json` 파일을 만든다.

```json
{
  "system_prompt": "짧게 답해줘"
}
```

요청:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" --data-binary "@request-bad.json"
```

예상 상태코드:

```text
HTTP/1.1 422 Unprocessable Entity
```

의미:

```text
ChatRequest schema에서 message 필드는 필수값이다.
message가 없으므로 FastAPI가 422 에러를 반환한다.
```

---

### Docker 로그 확인

```powershell
docker logs llm-api-local
```

실시간 로그 확인:

```powershell
docker logs -f llm-api-local
```

실시간 로그에서 빠져나오기:

```text
Ctrl + C
```

예상 로그:

```text
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     172.x.x.x:xxxxx - "GET /health HTTP/1.1" 200 OK
INFO:     172.x.x.x:xxxxx - "POST /chat HTTP/1.1" 200 OK
```

---

### Docker image tag 연습

현재 image 확인:

```powershell
docker images
```

새 tag 붙이기:

```powershell
docker tag llm-api:local llm-api:day2
```

다시 확인:

```powershell
docker images
```

의미:

```text
새 image를 다시 만든 것이 아니라,
기존 image에 이름표를 하나 더 붙인 것이다.
```

토요일 ECR에 push할 때도 같은 방식으로 ECR 주소를 tag로 붙인다.

```powershell
docker tag llm-api:local "$ECR_URI:latest"
```

---

### 유용한 Docker 명령어

```powershell
docker ps
docker images
docker logs llm-api-local
docker logs -f llm-api-local
docker stop llm-api-local
```

---

### 오늘 배운 핵심

```text
Dockerfile:
  Docker image를 만드는 설계도

Docker image:
  코드, Python, 설치된 패키지를 포함한 실행 가능한 패키지

Docker container:
  Docker image를 실제로 실행한 프로세스

-p 8000:8000:
  내 PC의 8000번 포트를 컨테이너 내부 8000번 포트에 연결

--env-file .env:
  .env 파일의 값을 컨테이너 실행 시점에 환경변수로 주입
```

---

### 중요한 습관

`.env` 파일은 Docker image 안에 복사하지 않는다.

```text
좋은 방식:
  image에는 코드와 패키지만 넣는다.
  환경변수는 실행 시점에 주입한다.

로컬 Docker:
  --env-file .env

ECS:
  Task Definition environment variables
  또는 Secrets Manager
```

이 습관이 중요한 이유:

```text
AWS 키, API key, Bedrock model id 같은 민감한 값이 image 안에 박히는 것을 막을 수 있다.
```

---

### 다음 단계

다음 단계에서는 오늘 만든 Docker image를 AWS에 올린다.

```text
llm-api:local
  ↓
Amazon ECR
  ↓
Amazon ECS Fargate
  ↓
Application Load Balancer
  ↓
GET /health
```

## Day 3 - AWS 계정 없이 배포 준비

### 목표

AWS 계정을 사용할 수 없는 날이므로, 실제 리소스를 생성하지 않고 토요일/일요일/월요일 실습을 위한 명령어와 설정값을 정리했다.

### 오늘 한 일

- Docker image `llm-api:local` 확인
- 로컬 Docker container에서 `/health`, `/chat` 확인
- ECR push 명령어 정리
- ECS 콘솔 설정값 정리
- ALB health check 설정값 정리
- task execution role과 task role 차이 정리
- Bedrock 연동 준비 문서 작성
- Bedrock task role policy 초안 작성

### AWS 배포 목표 흐름

```text
llm-api:local
  ↓
Amazon ECR
  ↓
Amazon ECS Fargate
  ↓
Application Load Balancer
  ↓
GET /health
```

### Bedrock 연동 목표 흐름

```text
FastAPI /chat
  ↓
Boto3 bedrock-runtime
  ↓
Bedrock Claude
  ↓
응답 반환
```

### 핵심 개념

```text
Task execution role:
  ECS가 ECR image pull, CloudWatch Logs 전송에 사용하는 role

Task role:
  컨테이너 안의 FastAPI 코드가 Bedrock 같은 AWS 서비스를 호출할 때 사용하는 role
```

암기 문장:

```text
execution role은 ECS가 쓰는 권한,
task role은 내 코드가 쓰는 권한.
```

### 다음 AWS 사용 가능일에 할 일

```text
[ ] aws sts get-caller-identity
[ ] ECR repository 생성
[ ] Docker image push
[ ] ECS Task Definition 생성
[ ] ECS Service 생성
[ ] ALB 연결
[ ] /health 외부 호출 성공
```