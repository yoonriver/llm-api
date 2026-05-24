## Troubleshooting - Bedrock AccessDeniedException

### 문제

ECS에 배포한 FastAPI `/chat` API에서 Bedrock Converse 호출 시 `AccessDeniedException` 발생.

CloudWatch Logs:

```text
botocore.errorfactory.AccessDeniedException:
An error occurred (AccessDeniedException) when calling the Converse operation:
User: arn:aws:sts::851725422006:assumed-role/llm-api-bedrock-task-role
```

### 원인

FastAPI 코드가 Bedrock을 호출할 때 사용하는 ECS task role에 Bedrock invoke 권한이 부족했다.

### 확인한 것

```text
FastAPI route:
  /chat

호출 코드:
  self.client.converse(**request)

실제 호출 주체:
  assumed-role/llm-api-bedrock-task-role
```

### 해결

`llm-api-bedrock-task-role`에 아래 inline policy 추가.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowBedrockInvokeForPractice",
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

이후 ECS Service에서 `Force new deployment` 실행.

### 배운 점

```text
Task execution role은 ECS가 ECR image pull, CloudWatch Logs 전송에 사용한다.
Task role은 컨테이너 안의 애플리케이션 코드가 AWS 서비스를 호출할 때 사용한다.
Bedrock 호출 권한은 task execution role이 아니라 task role에 붙여야 한다.
```