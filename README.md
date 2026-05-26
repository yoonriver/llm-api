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

## Day 4 - ECR 실습

### 목표

로컬 Docker image `llm-api:local`을 `us-east-1` region의 Amazon ECR에 push한다.

### 진행 흐름

```text
llm-api:local
  ↓ docker tag
<account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-api:latest
  ↓ docker push
Amazon ECR
```

### 사용한 명령어

```powershell
$REGION="us-east-1"
$APP_NAME="llm-api"
$ACCOUNT_ID = (aws sts get-caller-identity | ConvertFrom-Json).Account
$REGISTRY = "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
$ECR_URI = "${REGISTRY}/${APP_NAME}"

aws ecr create-repository `
  --repository-name $APP_NAME `
  --region $REGION

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $REGISTRY

docker tag llm-api:local "${ECR_URI}:latest"

docker push "${ECR_URI}:latest"

aws ecr describe-images `
  --repository-name $APP_NAME `
  --region $REGION
```

### 결과

```text
AWS 인증:
  성공

Region:
  us-east-1

ECR repository 생성:
  성공 / 이미 존재

ECR login:
  성공

Docker tag:
  성공

Docker push:
  성공

ECR image 확인:
  latest tag 확인
```

### 오늘 배운 것

```text
ECR은 region별 image 저장소다.
이번 실습 계정은 us-east-1 기준이므로 ECR repository도 us-east-1에 만들었다.
ECS에서 사용할 image URI는 <account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-api:latest 형태다.
```

## Day 4 - ECS/Fargate/ALB 배포

### 목표

ECR에 push한 FastAPI Docker image를 ECS Fargate에서 실행하고, ALB를 통해 `/health`, `/chat`을 호출한다.

### Region

```text
us-east-1
```

### 사용한 ECR image

```text
<account-id>.dkr.ecr.us-east-1.amazonaws.com/llm-api:latest
```

### 구성

```text
ECR:
  llm-api

ECS Cluster:
  llm-api-cluster

Task Definition:
  llm-api-task

ECS Service:
  llm-api-service

ALB:
  llm-api-alb

Target Group:
  llm-api-tg

Container Port:
  8000

Health Check Path:
  /health
```

### 흐름

```text
Client
  ↓ HTTP 80
Application Load Balancer
  ↓ HTTP 8000
ECS Fargate Task
  ↓
FastAPI /health, /chat
```

### 결과

```text
ECR push:
  성공 / 실패

ECS task running:
  성공 / 실패

CloudWatch Logs:
  확인함 / 확인 못함

Target group healthy:
  성공 / 실패

ALB /health:
  성공 / 실패

ALB /chat mock:
  성공 / 실패
```

### 오늘 배운 것

```text
ECR은 Docker image 저장소다.
ECS는 container 실행 관리자다.
Task Definition은 container 실행 설계도다.
ECS Service는 task를 계속 running 상태로 유지한다.
Fargate는 EC2 서버를 직접 관리하지 않고 container를 실행하는 방식이다.
ALB는 외부 HTTP 요청을 ECS task로 전달하는 입구다.
Target Group은 ALB가 요청을 보낼 대상 목록이다.
Health Check는 target이 살아 있는지 확인하는 검사다.
Fargate task의 target group target type은 ip로 설정해야 한다.
```

## Day 5 - Bedrock Claude 연동 완료

### 목표

FastAPI `/chat` API가 mock 응답이 아니라 AWS Bedrock Claude 응답을 반환하도록 만든다.

### 최종 흐름

```text
Client
  ↓ HTTP 80
Application Load Balancer
  ↓ HTTP 8000
ECS Fargate Task
  ↓
FastAPI /chat
  ↓
AWS Bedrock Claude
  ↓
응답 반환
```

### Region

```text
us-east-1
```

### ECS 환경변수

```text
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=실제_MODEL_ID
USE_BEDROCK=true
```

### IAM 정리

```text
Task execution role:
  ECS가 ECR image pull, CloudWatch Logs 전송에 사용

Task role:
  FastAPI 코드가 Bedrock 호출에 사용
```

### 해결한 문제

```text
문제:
  Bedrock Converse 호출 시 AccessDeniedException 발생

원인:
  llm-api-bedrock-task-role에 Bedrock invoke 권한이 부족했음

해결:
  task role에 bedrock:InvokeModel 권한 추가 후 ECS Service force new deployment 수행
```

### 결과

```text
Bedrock 단독 호출:
  성공

로컬 FastAPI /chat → Bedrock:
  성공

ECR bedrock image push:
  성공

ECS 새 revision 배포:
  성공

ALB /chat → Bedrock:
  성공
```

### 오늘 배운 것

```text
Bedrock Runtime은 실제 모델 호출에 사용된다.
Converse API는 메시지 기반 대화형 요청을 보낼 때 사용한다.
FastAPI 코드가 Bedrock을 호출하려면 ECS task role에 bedrock:InvokeModel 권한이 필요하다.
Task execution role과 task role은 다르다.
USE_BEDROCK=true일 때 BedrockClaudeService를 사용한다.
```

## Day 5.5 - S3 / DynamoDB 실습

### 목표

FastAPI 앱에서 AWS S3와 DynamoDB를 직접 호출해본다.

이번 실습의 목표는 아래와 같다.

```text
1. S3 bucket 생성
2. DynamoDB table 생성
3. Python script로 S3 / DynamoDB 단독 호출
4. FastAPI endpoint로 S3 / DynamoDB 기능 추가
5. ECS task role에 S3 / DynamoDB 권한 추가
6. ALB를 통해 S3 / DynamoDB API 호출
```

---

### 최종 구조

```text
Client
  ↓ HTTP 80
Application Load Balancer
  ↓ HTTP 8000
ECS Fargate Task
  ↓
FastAPI
  ├─ S3
  │   └─ 텍스트/object 저장
  │
  └─ DynamoDB
      └─ 채팅 이력 메타데이터 저장
```

---

### S3 역할

S3는 파일/object 저장소로 사용했다.

이번 실습에서는 긴 텍스트나 artifact를 저장하는 용도로 사용했다.

```text
S3 Bucket:
  llm-api-artifacts-<ACCOUNT_ID>

S3 Object 예시:
  notes/day5/s3-fastapi-test.txt
```

구현한 API:

```text
POST /storage/s3/text
GET  /storage/s3/text/{object_key}
```

---

### DynamoDB 역할

DynamoDB는 채팅 이력 메타데이터 저장소로 사용했다.

이번 실습에서는 session 단위로 채팅 이력을 저장하고 조회하는 용도로 사용했다.

```text
Table:
  llm-chat-history

Partition key:
  session_id

Sort key:
  created_at
```

구현한 API:

```text
POST /history
GET  /history/{session_id}
```

---

### S3와 DynamoDB 차이

```text
S3:
  파일, 긴 텍스트, PDF, 이미지, HTML, parser artifact 저장에 적합하다.

DynamoDB:
  session_id, created_at, message, answer 같은 구조화된 이력/메타데이터 저장에 적합하다.
```

이번 실습에서는 이렇게 나누었다.

```text
S3:
  텍스트 object 저장

DynamoDB:
  채팅 이력 저장
```

---

### AWS 리소스

```text
Region:
  us-east-1

S3 Bucket:
  llm-api-artifacts-<ACCOUNT_ID>

DynamoDB Table:
  llm-chat-history

ECS Cluster:
  llm-api-cluster

ECS Service:
  llm-api-service

Task Role:
  llm-api-bedrock-task-role
```

---

### ECS 환경변수

ECS Task Definition에 아래 환경변수를 추가했다.

```text
AWS_REGION=us-east-1
S3_BUCKET=llm-api-artifacts-<ACCOUNT_ID>
DDB_TABLE=llm-chat-history
```

기존 Bedrock 환경변수도 유지했다.

```text
BEDROCK_MODEL_ID=<실제_MODEL_ID>
USE_BEDROCK=true
```

---

### IAM 권한

S3와 DynamoDB 호출 권한은 `task execution role`이 아니라 `task role`에 추가했다.

```text
Task execution role:
  ECS가 ECR image pull, CloudWatch Logs 전송에 사용

Task role:
  FastAPI 코드가 Bedrock, S3, DynamoDB를 호출할 때 사용
```

S3 / DynamoDB 권한은 아래 task role에 추가했다.

```text
llm-api-bedrock-task-role
```

---

### 최종 테스트 결과

```text
S3 bucket 생성:
  성공 / 실패

S3 put/get CLI 테스트:
  성공 / 실패

DynamoDB table 생성:
  성공 / 실패

DynamoDB put/query CLI 테스트:
  성공 / 실패

scripts/test_s3.py:
  성공 / 실패

scripts/test_dynamodb.py:
  성공 / 실패

로컬 FastAPI S3 endpoint:
  성공 / 실패

로컬 FastAPI DynamoDB endpoint:
  성공 / 실패

ECS/ALB S3 endpoint:
  성공 / 실패

ECS/ALB DynamoDB endpoint:
  성공 / 실패
```

---

### 오늘 배운 것

```text
S3는 파일/object 저장소다.
DynamoDB는 NoSQL key-value/document 데이터베이스다.
S3 object는 bucket + key로 식별한다.
DynamoDB item은 primary key로 식별한다.
이번 DynamoDB table은 session_id를 partition key, created_at을 sort key로 사용했다.
ECS에서 S3/DynamoDB를 호출하려면 task role에 권한을 추가해야 한다.
task execution role과 task role은 다르다.
```


## Day 6 - LangChain 기본

### 목표

AWS 계정 없이 LangChain의 기본 구조를 익히고, FastAPI에 `/chain/chat` API를 추가한다.

### 오늘 만든 흐름

```text
Client
  ↓
FastAPI /chain/chat
  ↓
ChatPromptTemplate
  ↓
FakeListChatModel
  ↓
StrOutputParser
  ↓
Response
```

### 사용한 주요 구성 요소

```text
ChatPromptTemplate:
  system message와 human message를 template으로 관리한다.

FakeListChatModel:
  실제 LLM 대신 정해진 응답을 반환하는 테스트용 chat model이다.

StrOutputParser:
  모델 응답을 문자열로 변환한다.
```

### API

```text
POST /chain/chat
```

요청 예시:

```json
{
  "message": "LangChain이 뭐야?",
  "tone": "초보자도 이해하기 쉽게"
}
```

응답 예시:

```json
{
  "answer": "LangChain mock 응답입니다. 실제 LLM 대신 테스트용 FakeListChatModel이 반환한 답변입니다.",
  "chain_type": "langchain-fake-chat"
}
```

### 테스트

```powershell
curl.exe -X POST http://127.0.0.1:8000/chain/chat -H "Content-Type: application/json" --data-binary "@request-chain-chat.json"
```

### 기존 Bedrock 직접 호출 방식과 비교

```text
기존 방식:
  FastAPI → boto3 bedrock-runtime → client.converse()

LangChain 방식:
  FastAPI → PromptTemplate → ChatModel → OutputParser
```

### 오늘 배운 것

```text
LangChain은 LLM 앱을 prompt, model, parser 단위로 나눠 구성할 수 있게 해준다.
단순 Bedrock 호출은 boto3 직접 호출로도 충분하다.
하지만 프롬프트, parser, tool, retriever, agent가 늘어나면 LangChain 구조가 유리해진다.
FakeListChatModel을 사용하면 실제 LLM 없이도 chain 구조를 테스트할 수 있다.
```

## Day 7 - LangGraph 기본 구현

### 목표

LangGraph의 기본 개념인 State, Node, Edge를 사용해 FastAPI에 `/agent/chat` API를 추가한다.

### 오늘 만든 흐름

```text
START
  ↓
classify_question
  ↓
generate_answer
  ↓
validate_answer
  ↓
END
```

### API

```text
POST /agent/chat
```

요청 예시:

```json
{
  "message": "LangGraph는 LangChain이랑 뭐가 달라?"
}
```

응답 예시:

```json
{
  "question_type": "llm_framework",
  "answer": "LangChain/LangGraph 관련 질문으로 분류했습니다...",
  "validated": true,
  "trace": [
    "classify_question:llm_framework",
    "generate_answer",
    "validate_answer:True"
  ]
}
```

### State

State는 그래프 전체를 흐르는 공유 데이터다.

```python
class AgentState(TypedDict):
    message: str
    question_type: str
    answer: str
    validated: bool
    trace: list[str]
```

### Node

Node는 실제 작업을 수행하는 함수다.

이번 실습에서는 세 개의 node를 만들었다.

```text
classify_question:
  질문 유형 분류

generate_answer:
  질문 유형에 따른 답변 생성

validate_answer:
  답변 검증
```

### Edge

Edge는 노드 간 실행 순서를 정한다.

```python
graph.add_edge(START, "classify_question")
graph.add_edge("classify_question", "generate_answer")
graph.add_edge("generate_answer", "validate_answer")
graph.add_edge("validate_answer", END)
```

### 오늘 배운 것

```text
LangGraph는 LLM 애플리케이션의 작업 흐름을 State, Node, Edge로 표현하는 workflow 도구다.
State는 들고 다니는 데이터다.
Node는 작업 함수다.
Edge는 다음 작업으로 가는 연결선이다.
LangChain은 LLM 호출 부품 조립에 가깝고, LangGraph는 LLM 작업 흐름 관리에 가깝다.
```