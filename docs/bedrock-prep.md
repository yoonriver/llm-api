# Bedrock 준비 노트

## 목표

FastAPI `/chat` API가 mock 응답이 아니라 AWS Bedrock Claude를 호출하도록 만든다.

최종 흐름:

```text
FastAPI /chat
  ↓
Boto3 bedrock-runtime
  ↓
Bedrock Claude
  ↓
응답 반환
```

---

## 1. 확인해야 할 것

AWS 계정 사용 가능일에 확인한다.

```text
[ ] Bedrock 사용 가능 region
[ ] Anthropic Claude model access
[ ] 사용할 model id
[ ] IAM 권한
```

---

## 2. `.env`에 추가할 값

```env
AWS_REGION=ap-northeast-2
BEDROCK_MODEL_ID=실제_MODEL_ID
USE_BEDROCK=true
```

로컬 mock 모드에서는:

```env
USE_BEDROCK=false
```

---

## 3. Bedrock 단독 호출 테스트 파일

파일 경로:

```text
scripts/test_bedrock.py
```

목표:

```text
FastAPI에 붙이기 전에 Python script로 Bedrock Claude 호출을 먼저 성공시킨다.
```

---

## 4. ECS에서 필요한 환경변수

ECS Task Definition에 추가할 값:

```text
AWS_REGION=ap-northeast-2
BEDROCK_MODEL_ID=실제_MODEL_ID
USE_BEDROCK=true
```

---

## 5. ECS Task Role 권한

FastAPI 코드가 Bedrock을 호출하려면 task role에 Bedrock 권한이 필요하다.

권한 초안:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "*"
    }
  ]
}
```

Streaming까지 사용할 경우 검토할 권한:

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModelWithResponseStream"
  ],
  "Resource": "*"
}
```

---

## 6. Role 구분

```text
Task execution role:
  ECS가 ECR image pull, CloudWatch Logs 전송에 사용

Task role:
  FastAPI 코드가 Bedrock 호출에 사용
```

암기 문장:

```text
execution role은 ECS가 쓰는 권한,
task role은 내 코드가 쓰는 권한.
```

---

## 7. Bedrock 연결 성공 기준

최소 성공:

```text
[ ] scripts/test_bedrock.py로 Claude 응답 받기
```

목표 성공:

```text
[ ] 로컬 FastAPI /chat에서 Claude 응답 받기
```

최고 성공:

```text
[ ] ECS ALB URL /chat에서 Claude 응답 받기
```