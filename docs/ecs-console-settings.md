# ECS 콘솔 설정값 정리

## 목표

ECR에 push한 FastAPI Docker image를 ECS Fargate에서 실행한다.

최종 흐름:

```text
ECR image
  ↓
ECS Fargate Task
  ↓
ECS Service
  ↓
Application Load Balancer
  ↓
/health
```

---

## 1. ECS Cluster

```text
Cluster name:
  llm-api-cluster

Infrastructure:
  AWS Fargate
```

---

## 2. Task Definition

```text
Task definition family:
  llm-api-task

Launch type:
  Fargate

CPU:
  0.25 vCPU 또는 0.5 vCPU

Memory:
  0.5GB 또는 1GB
```

---

## 3. Container 설정

```text
Container name:
  llm-api

Image URI:
  <ECR_URI>:latest

Container port:
  8000

Protocol:
  TCP
```

환경변수:

```text
APP_NAME=Bedrock Claude FastAPI Server
ENVIRONMENT=dev
MOCK_MODEL_NAME=mock-claude
```

---

## 4. Logging

```text
Log driver:
  awslogs

Log group:
  /ecs/llm-api

Log stream prefix:
  ecs
```

확인할 로그:

```text
[ ] Uvicorn 실행 로그
[ ] GET /health 요청 로그
[ ] POST /chat 요청 로그
```

---

## 5. IAM Role

### Task execution role

ECS가 컨테이너를 실행할 때 사용하는 role이다.

필요한 작업:

```text
ECR image pull
CloudWatch Logs 전송
```

암기:

```text
Task execution role = ECS가 쓰는 권한
```

---

### Task role

컨테이너 안의 애플리케이션 코드가 AWS 서비스를 호출할 때 사용하는 role이다.

예:

```text
FastAPI 코드가 Bedrock 호출
FastAPI 코드가 S3 접근
FastAPI 코드가 Secrets Manager 접근
```

암기:

```text
Task role = 내 코드가 쓰는 권한
```

---

## 6. ECS Service

```text
Service name:
  llm-api-service

Desired tasks:
  1

Launch type:
  Fargate
```

---

## 7. Load Balancer

```text
Load balancer type:
  Application Load Balancer

Listener:
  HTTP 80

Target group protocol:
  HTTP

Target group port:
  8000

Health check path:
  /health
```

---

## 8. Security Group

### ALB Security Group

```text
Inbound:
  HTTP 80 from 0.0.0.0/0
```

### ECS Task Security Group

```text
Inbound:
  TCP 8000 from ALB Security Group
```

---

## 9. 최종 테스트

ALB DNS로 호출:

```powershell
curl.exe http://ALB-DNS-NAME/health
```

예상 응답:

```json
{
  "status": "ok"
}
```

`/chat` mock 테스트:

```powershell
curl.exe -X POST http://ALB-DNS-NAME/chat -H "Content-Type: application/json" --data-binary "@request-chat.json"
```

---

## 10. 장애 확인 순서

### ECS task가 바로 죽는 경우

```text
1. CloudWatch Logs 확인
2. Dockerfile CMD 확인
3. requirements.txt 확인
4. uvicorn host가 0.0.0.0인지 확인
```

### ALB health check 실패

```text
1. Health check path가 /health인지 확인
2. Target port가 8000인지 확인
3. ECS task security group이 ALB에서 오는 8000을 허용하는지 확인
4. 컨테이너가 실제로 8000번에서 실행 중인지 확인
```

### 외부 접속 실패

```text
1. ALB Listener가 HTTP 80인지 확인
2. ALB security group inbound 80 확인
3. Target group에 healthy target이 있는지 확인
4. ECS service가 running인지 확인
```