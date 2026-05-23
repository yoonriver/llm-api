# Load Balancer 정리

## 1. 이번 실습에서 Load Balancer가 필요한 이유

이번 FastAPI 앱은 ECS Fargate 안에서 실행된다.

컨테이너 내부에서는 FastAPI가 8000번 포트로 실행된다.

```text
FastAPI container
  → 0.0.0.0:8000
```

하지만 사용자가 ECS task에 직접 접근하게 두는 방식은 좋지 않다.

그래서 앞단에 Application Load Balancer, 즉 ALB를 둔다.

```text
사용자
  ↓ HTTP 80
Application Load Balancer
  ↓ HTTP 8000
ECS Fargate Task
  ↓
FastAPI /health, /chat
```

즉, ALB는 외부 요청을 받아서 ECS task로 전달하는 입구 역할을 한다.

---

## 2. 이번 실습 전체 흐름

```text
Client
  ↓
ALB Listener: HTTP 80
  ↓
Target Group: HTTP 8000
  ↓
ECS Fargate Task
  ↓
FastAPI container: port 8000
  ↓
GET /health
POST /chat
```

이번 실습의 핵심 설정은 아래와 같다.

```text
Region:
  us-east-1

ALB name:
  llm-api-alb

Listener:
  HTTP 80

Target Group:
  llm-api-tg

Target type:
  IP

Target port:
  8000

Health check path:
  /health

ECS Service:
  llm-api-service

Container port:
  8000
```

---

## 3. ALB란?

ALB는 Application Load Balancer의 약자다.

쉽게 말하면:

```text
외부 HTTP 요청을 받아서 실제 서버 역할을 하는 target으로 보내주는 입구
```

이번 실습에서는 target이 ECS Fargate task다.

```text
사용자 요청
  ↓
ALB
  ↓
ECS Fargate Task
```

ALB를 쓰는 이유:

```text
1. 외부 사용자가 접근할 주소를 제공한다.
2. ECS task가 바뀌어도 ALB 주소는 유지된다.
3. target이 정상인지 health check로 확인한다.
4. 정상 target에만 요청을 보낸다.
5. 나중에 task가 여러 개가 되면 요청을 분산할 수 있다.
```

---

## 4. Listener란?

Listener는 ALB가 어떤 포트에서 요청을 받을지 정하는 설정이다.

이번 실습에서는:

```text
Listener:
  HTTP 80
```

뜻:

```text
사용자가 http://ALB-DNS-NAME 으로 요청하면
ALB가 80번 포트에서 요청을 받는다.
```

예:

```powershell
curl.exe http://llm-api-alb-xxxx.us-east-1.elb.amazonaws.com/health
```

여기서 사용자는 8000번 포트로 직접 접근하지 않는다.

사용자는 ALB의 80번 포트로 접근한다.

```text
사용자 → ALB: 80
ALB → ECS task: 8000
```

---

## 5. Target Group이란?

Target Group은 ALB가 요청을 전달할 대상 목록이다.

이번 실습에서는 ALB가 요청을 보낼 대상이 ECS Fargate task다.

```text
ALB
  ↓
Target Group
  ↓
ECS Fargate Task
```

이번 실습의 Target Group 설정:

```text
Target group name:
  llm-api-tg

Protocol:
  HTTP

Port:
  8000

Target type:
  IP

Health check path:
  /health
```

여기서 중요한 값은 세 개다.

```text
1. Target type = IP
2. Port = 8000
3. Health check path = /health
```

---

## 6. 왜 Target type이 IP여야 하나?

ECS Fargate task는 EC2 instance 위에 직접 붙어서 관리하는 방식이 아니다.

Fargate task는 자체 네트워크 인터페이스를 가진다.

그래서 target group에서 target type을 `instance`가 아니라 `ip`로 설정해야 한다.

```text
EC2 기반 ECS:
  target type = instance를 쓰는 경우가 있음

Fargate 기반 ECS:
  target type = ip
```

이번 실습은 Fargate이므로:

```text
Target type:
  IP addresses
```

또는 콘솔에서:

```text
Target type:
  ip
```

로 설정한다.

---

## 7. Health Check란?

Health Check는 ALB가 ECS task가 살아 있는지 확인하는 검사다.

이번 실습에서는 ALB가 주기적으로 아래 요청을 보낸다.

```text
GET /health
```

FastAPI 앱은 이 요청에 이렇게 응답한다.

```json
{
  "status": "ok"
}
```

정상 응답이 오면 target 상태가 healthy가 된다.

```text
Target Group
  → Targets
  → healthy
```

만약 `/health`가 없거나, 포트가 틀리거나, Security Group이 막혀 있으면 target은 unhealthy가 된다.

```text
Target Group
  → Targets
  → unhealthy
```

---

## 8. 이번 실습에서 Health Check 설정

Target Group의 health check 설정은 아래처럼 둔다.

```text
Protocol:
  HTTP

Path:
  /health

Port:
  traffic port 또는 8000

Expected response:
  200
```

FastAPI 쪽 API:

```text
GET /health
```

응답:

```json
{
  "status": "ok"
}
```

중요한 점:

```text
Health check path는 /health여야 한다.
Target group port는 8000이어야 한다.
Container port도 8000이어야 한다.
```

---

## 9. Security Group이란?

Security Group은 AWS 리소스의 방화벽이다.

이번 실습에서는 Security Group이 두 종류 필요하다.

```text
1. ALB Security Group
2. ECS Task Security Group
```

---

## 10. ALB Security Group

ALB는 외부 사용자의 HTTP 요청을 받아야 한다.

그래서 ALB Security Group의 inbound rule은 아래처럼 둔다.

```text
Inbound:
  Type: HTTP
  Protocol: TCP
  Port: 80
  Source: 0.0.0.0/0
```

뜻:

```text
인터넷에서 ALB의 80번 포트로 접근 가능하다.
```

---

## 11. ECS Task Security Group

ECS task는 인터넷에서 직접 접근하지 않게 한다.

대신 ALB에서 오는 요청만 허용한다.

```text
Inbound:
  Type: Custom TCP
  Protocol: TCP
  Port: 8000
  Source: ALB Security Group
```

뜻:

```text
ALB만 ECS task의 8000번 포트로 접근할 수 있다.
```

전체 흐름:

```text
사용자
  ↓ HTTP 80
ALB Security Group
  ↓ TCP 8000
ECS Task Security Group
  ↓
FastAPI container
```

주의할 점:

```text
ECS Task Security Group의 inbound를 80으로 열면 안 된다.
FastAPI container는 8000번에서 실행 중이므로 ECS Task inbound는 8000이어야 한다.
```

---

## 12. 왜 사용자는 80번인데 ECS는 8000번인가?

사용자는 ALB에 접근한다.

```text
사용자 → ALB: 80
```

ALB는 ECS task로 요청을 전달한다.

```text
ALB → ECS Task: 8000
```

FastAPI는 container 안에서 8000번 포트로 실행된다.

```text
FastAPI container: 8000
```

그래서 포트 구조는 아래처럼 이해하면 된다.

```text
외부 공개 포트:
  ALB 80

애플리케이션 내부 포트:
  ECS Task 8000
  FastAPI container 8000
```

---

## 13. 이번 실습의 실제 설정 요약

```text
ALB:
  llm-api-alb

Listener:
  HTTP 80

Target Group:
  llm-api-tg

Target type:
  IP

Target protocol:
  HTTP

Target port:
  8000

Health check path:
  /health

ECS Service:
  llm-api-service

ECS Task container port:
  8000

FastAPI 실행 포트:
  8000
```

---

## 14. 요청이 실제로 흐르는 순서

사용자가 `/health`를 호출한다.

```powershell
curl.exe http://ALB-DNS-NAME/health
```

요청 흐름:

```text
1. 사용자가 ALB DNS로 요청
2. ALB Listener가 HTTP 80에서 요청 수신
3. ALB가 listener rule에 따라 target group으로 요청 전달
4. Target Group이 healthy 상태의 ECS task를 선택
5. ALB가 ECS task의 8000번 포트로 요청 전달
6. FastAPI가 /health 요청 처리
7. FastAPI가 {"status": "ok"} 응답
8. ALB가 사용자에게 응답 반환
```

---

## 15. /chat 요청 흐름

```powershell
curl.exe -X POST http://ALB-DNS-NAME/chat -H "Content-Type: application/json" --data-binary "@request-chat.json"
```

요청 흐름:

```text
1. 사용자가 ALB DNS로 POST /chat 요청
2. ALB가 HTTP 80에서 요청 수신
3. Target Group을 통해 ECS task의 8000번 포트로 요청 전달
4. FastAPI /chat route가 요청 처리
5. MockLLMService가 mock 답변 생성
6. 응답이 ALB를 거쳐 사용자에게 반환
```

---

## 16. Target Group이 unhealthy일 때 확인할 것

Target Group이 unhealthy면 아래 순서대로 확인한다.

```text
1. FastAPI에 /health API가 있는가?
2. /health가 200 응답을 반환하는가?
3. Target Group health check path가 /health인가?
4. Target Group port가 8000인가?
5. Target type이 ip인가?
6. ECS Task Definition의 container port가 8000인가?
7. ECS Task Security Group이 ALB Security Group에서 오는 8000번을 허용하는가?
8. CloudWatch Logs에 Uvicorn 실행 로그가 있는가?
```

---

## 17. ALB URL 접속이 안 될 때 확인할 것

```text
1. ALB Listener가 HTTP 80인가?
2. ALB Security Group inbound에 HTTP 80 from 0.0.0.0/0이 있는가?
3. Target Group에 healthy target이 있는가?
4. ECS Service의 Running task가 1개인가?
5. ALB DNS를 정확히 사용했는가?
6. http:// 로 요청했는가?
```

주의:

```text
이번 실습은 HTTPS가 아니라 HTTP 80이다.
따라서 https:// 가 아니라 http:// 로 호출한다.
```

---

## 18. ECS task는 running인데 ALB가 안 되는 경우

이 경우는 보통 애플리케이션 문제보다 네트워크/로드밸런서 설정 문제다.

확인 순서:

```text
1. CloudWatch Logs에서 FastAPI가 실행 중인지 확인
2. Target Group health 확인
3. Security Group 확인
4. Listener와 Target Group 연결 확인
5. Health check path 확인
```

CloudWatch Logs에 아래 로그가 있으면 FastAPI 자체는 떠 있는 것이다.

```text
Uvicorn running on http://0.0.0.0:8000
```

그런데 Target Group이 unhealthy라면 보통 아래 중 하나다.

```text
Health check path 문제
Port 문제
Security Group 문제
Target type 문제
```

---

## 19. 로드밸런서 관련 암기 문장

```text
ALB는 외부 요청을 받는 입구다.
Listener는 ALB가 요청을 받을 포트다.
Target Group은 ALB가 요청을 보낼 대상 목록이다.
Health Check는 target이 살아 있는지 검사하는 요청이다.
Fargate ECS task는 target type을 ip로 설정해야 한다.
사용자는 ALB 80번 포트로 접근하고, ALB는 ECS task 8000번 포트로 전달한다.
ECS task security group은 ALB security group에서 오는 8000번만 허용한다.
```

---

## 20. 이번 실습 성공 기준

```text
[ ] Target Group 상태가 healthy
[ ] ALB DNS로 /health 호출 성공
[ ] ALB DNS로 /chat mock 호출 성공
[ ] CloudWatch Logs에서 GET /health 200 확인
[ ] CloudWatch Logs에서 POST /chat 200 확인
```

---

## 21. 최종 테스트 명령어

Health check:

```powershell
curl.exe http://ALB-DNS-NAME/health
```

예상 응답:

```json
{
  "status": "ok"
}
```

Chat mock:

```powershell
curl.exe -X POST http://ALB-DNS-NAME/chat -H "Content-Type: application/json" --data-binary "@request-chat.json"
```

예상 응답:

```json
{
  "answer": "[mock] ...",
  "model": "mock-claude"
}
```