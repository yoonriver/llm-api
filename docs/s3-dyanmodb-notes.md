# S3 / DynamoDB 실습 노트

## 1. 실습 목표

이번 실습의 목표는 FastAPI 앱에서 AWS S3와 DynamoDB를 직접 호출해보는 것이다.

기존 프로젝트 흐름은 아래와 같았다.

```text
Client
  ↓
ALB
  ↓
ECS Fargate
  ↓
FastAPI
  ↓
Bedrock Claude
```

이번 실습에서는 여기에 S3와 DynamoDB를 추가한다.

```text
Client
  ↓
ALB
  ↓
ECS Fargate
  ↓
FastAPI
  ├─ Bedrock Claude
  ├─ S3
  └─ DynamoDB
```

---

## 2. S3 개념

S3는 파일/object 저장소다.

쉽게 말하면:

```text
S3 Bucket:
  파일을 담는 큰 저장 공간

S3 Object:
  bucket 안에 저장된 파일 또는 데이터

S3 Object Key:
  object의 경로/이름
```

예:

```text
Bucket:
  llm-api-artifacts-851725422006

Object Key:
  notes/day5/s3-fastapi-test.txt
```

전체 주소 느낌:

```text
s3://llm-api-artifacts-851725422006/notes/day5/s3-fastapi-test.txt
```

---

## 3. S3를 사용하는 이유

S3는 아래 같은 데이터를 저장하기 좋다.

```text
PDF
이미지
HTML
JSON
텍스트 파일
parser artifact
대용량 결과물
로그성 파일
Athena query result
Iceberg table file
```

이번 실습에서는 간단히 텍스트 object를 저장했다.

```text
POST /storage/s3/text
  → S3에 텍스트 저장

GET /storage/s3/text/{object_key}
  → S3에서 텍스트 읽기
```

---

## 4. DynamoDB 개념

DynamoDB는 AWS의 NoSQL 데이터베이스다.

쉽게 말하면:

```text
Table:
  데이터를 저장하는 표

Item:
  table 안의 한 줄 데이터

Attribute:
  item 안의 필드

Primary Key:
  item을 식별하는 키
```

예시 item:

```json
{
  "session_id": "session-fastapi-test",
  "created_at": "2026-05-24T00:00:00Z",
  "chat_id": "uuid-value",
  "message": "S3와 DynamoDB 차이가 뭐야?",
  "answer": "S3는 파일 저장소이고 DynamoDB는 NoSQL 데이터베이스입니다."
}
```

---

## 5. DynamoDB를 사용하는 이유

DynamoDB는 아래 같은 데이터에 적합하다.

```text
채팅 이력
사용자별 상태
session 기반 기록
빠른 key-value 조회
간단한 메타데이터
이벤트성 데이터
```

이번 실습에서는 채팅 이력을 저장했다.

```text
POST /history
  → 채팅 이력 저장

GET /history/{session_id}
  → session_id 기준으로 채팅 이력 조회
```

---

## 6. S3와 DynamoDB 차이

```text
S3:
  파일/object 저장에 적합하다.
  object key로 파일을 찾는다.
  대용량 데이터 저장에 좋다.

DynamoDB:
  NoSQL database다.
  primary key로 item을 찾는다.
  session_id, timestamp, 상태값 같은 메타데이터 저장에 좋다.
```

이번 실습에서는 이렇게 역할을 나누었다.

```text
S3:
  텍스트 object 저장

DynamoDB:
  채팅 이력 메타데이터 저장
```

---

## 7. 생성한 AWS 리소스

### Region

```text
us-east-1
```

### S3

```text
Bucket name:
  llm-api-artifacts-<ACCOUNT_ID>
```

예:

```text
llm-api-artifacts-851725422006
```

### DynamoDB

```text
Table name:
  llm-chat-history

Partition key:
  session_id

Sort key:
  created_at

Billing mode:
  PAY_PER_REQUEST
```

---

## 8. DynamoDB Table 설계

이번 table은 아래 key 구조를 사용했다.

```text
Partition key:
  session_id

Sort key:
  created_at
```

이렇게 설계한 이유:

```text
하나의 session_id 안에 여러 채팅 메시지가 저장될 수 있다.
created_at을 sort key로 두면 같은 session의 대화 이력을 시간순으로 조회할 수 있다.
```

예:

```text
session_id = session-001
  ├─ created_at = 2026-05-24T00:00:00Z
  ├─ created_at = 2026-05-24T00:01:00Z
  └─ created_at = 2026-05-24T00:02:00Z
```

조회 패턴:

```text
특정 session_id의 전체 채팅 이력 조회
```

사용 API:

```text
Query
```

---

## 9. AWS CLI - 변수 설정

PowerShell에서 아래 변수를 사용했다.

```powershell
$REGION="us-east-1"
$APP_NAME="llm-api"
$ACCOUNT_ID = (aws sts get-caller-identity | ConvertFrom-Json).Account
$S3_BUCKET="llm-api-artifacts-$ACCOUNT_ID"
$DDB_TABLE="llm-chat-history"
```

확인:

```powershell
$ACCOUNT_ID
$S3_BUCKET
$DDB_TABLE
```

예상:

```text
851725422006
llm-api-artifacts-851725422006
llm-chat-history
```

---

## 10. AWS CLI - S3 bucket 생성

us-east-1에서는 `LocationConstraint`를 넣지 않고 bucket을 생성했다.

```powershell
aws s3api create-bucket `
  --bucket $S3_BUCKET `
  --region $REGION
```

bucket 확인:

```powershell
aws s3api head-bucket `
  --bucket $S3_BUCKET
```

---

## 11. AWS CLI - S3 put/get 테스트

테스트 파일 생성:

```powershell
"hello s3 from llm-api" | Set-Content -Path s3-test.txt -Encoding utf8
```

S3 업로드:

```powershell
aws s3 cp s3-test.txt "s3://$S3_BUCKET/test/s3-test.txt"
```

S3에서 내용 읽기:

```powershell
aws s3 cp "s3://$S3_BUCKET/test/s3-test.txt" -
```

성공 기준:

```text
[ ] s3-test.txt 업로드 성공
[ ] S3에서 파일 내용 조회 성공
```

---

## 12. AWS CLI - DynamoDB table 생성

```powershell
aws dynamodb create-table `
  --table-name $DDB_TABLE `
  --attribute-definitions `
      AttributeName=session_id,AttributeType=S `
      AttributeName=created_at,AttributeType=S `
  --key-schema `
      AttributeName=session_id,KeyType=HASH `
      AttributeName=created_at,KeyType=RANGE `
  --billing-mode PAY_PER_REQUEST `
  --region $REGION
```

Table 상태 확인:

```powershell
aws dynamodb describe-table `
  --table-name $DDB_TABLE `
  --region $REGION
```

확인할 값:

```text
TableStatus:
  ACTIVE
```

---

## 13. AWS CLI - DynamoDB put/query 테스트

Item 저장:

```powershell
aws dynamodb put-item `
  --table-name $DDB_TABLE `
  --item '{
    "session_id": {"S": "session-cli-test"},
    "created_at": {"S": "2026-05-24T00:00:00Z"},
    "message": {"S": "CLI 테스트"},
    "answer": {"S": "DynamoDB 저장 성공"}
  }' `
  --region $REGION
```

session_id 기준 조회:

```powershell
aws dynamodb query `
  --table-name $DDB_TABLE `
  --key-condition-expression "session_id = :sid" `
  --expression-attribute-values '{":sid":{"S":"session-cli-test"}}' `
  --region $REGION
```

성공 기준:

```text
[ ] put-item 성공
[ ] query 결과에 session-cli-test item이 보임
```

---

## 14. .env 설정

`.env`에 아래 값을 추가했다.

```env
S3_BUCKET=llm-api-artifacts-<ACCOUNT_ID>
DDB_TABLE=llm-chat-history
```

전체 예:

```env
APP_NAME=Bedrock Claude FastAPI Server
ENVIRONMENT=local
MOCK_MODEL_NAME=mock-claude

AWS_REGION=us-east-1
BEDROCK_MODEL_ID=<실제_MODEL_ID>
USE_BEDROCK=true

S3_BUCKET=llm-api-artifacts-<ACCOUNT_ID>
DDB_TABLE=llm-chat-history
```

---

## 15. Python script - S3 테스트

파일:

```text
scripts/test_s3.py
```

역할:

```text
FastAPI에 붙이기 전에 boto3로 S3 put/get이 되는지 검증한다.
```

성공 기준:

```text
[ ] S3에 object 저장
[ ] 저장한 object 다시 읽기
[ ] bucket, key, content 출력
```

실행:

```powershell
python scripts\test_s3.py
```

---

## 16. Python script - DynamoDB 테스트

파일:

```text
scripts/test_dynamodb.py
```

역할:

```text
FastAPI에 붙이기 전에 boto3로 DynamoDB put/query가 되는지 검증한다.
```

성공 기준:

```text
[ ] DynamoDB table에 item 저장
[ ] session_id 기준 query 성공
[ ] 저장한 item이 출력됨
```

실행:

```powershell
python scripts\test_dynamodb.py
```

---

## 17. FastAPI에 추가한 endpoint

### S3

```text
POST /storage/s3/text
GET  /storage/s3/text/{object_key}
```

### DynamoDB

```text
POST /history
GET  /history/{session_id}
```

---

## 18. S3 API 테스트

요청 파일:

```text
request-s3-put.json
```

내용:

```json
{
  "object_key": "notes/day5/s3-fastapi-test.txt",
  "content": "FastAPI에서 S3로 저장한 텍스트입니다."
}
```

S3 저장 요청:

```powershell
curl.exe -X POST http://127.0.0.1:8000/storage/s3/text -H "Content-Type: application/json" --data-binary "@request-s3-put.json"
```

예상 응답:

```json
{
  "bucket": "llm-api-artifacts-<ACCOUNT_ID>",
  "object_key": "notes/day5/s3-fastapi-test.txt",
  "status": "saved"
}
```

S3 조회 요청:

```powershell
curl.exe http://127.0.0.1:8000/storage/s3/text/notes/day5/s3-fastapi-test.txt
```

예상 응답:

```json
{
  "bucket": "llm-api-artifacts-<ACCOUNT_ID>",
  "object_key": "notes/day5/s3-fastapi-test.txt",
  "content": "FastAPI에서 S3로 저장한 텍스트입니다."
}
```

---

## 19. DynamoDB API 테스트

요청 파일:

```text
request-history-put.json
```

내용:

```json
{
  "session_id": "session-fastapi-test",
  "message": "S3와 DynamoDB 차이가 뭐야?",
  "answer": "S3는 파일 저장소이고 DynamoDB는 NoSQL 데이터베이스입니다."
}
```

DynamoDB 저장 요청:

```powershell
curl.exe -X POST http://127.0.0.1:8000/history -H "Content-Type: application/json" --data-binary "@request-history-put.json"
```

예상 응답:

```json
{
  "item": {
    "session_id": "session-fastapi-test",
    "created_at": "2026-05-24T...",
    "chat_id": "...",
    "message": "S3와 DynamoDB 차이가 뭐야?",
    "answer": "S3는 파일 저장소이고 DynamoDB는 NoSQL 데이터베이스입니다."
  }
}
```

DynamoDB 조회 요청:

```powershell
curl.exe http://127.0.0.1:8000/history/session-fastapi-test
```

예상 응답:

```json
{
  "session_id": "session-fastapi-test",
  "items": [
    {
      "session_id": "session-fastapi-test",
      "created_at": "2026-05-24T...",
      "chat_id": "...",
      "message": "S3와 DynamoDB 차이가 뭐야?",
      "answer": "S3는 파일 저장소이고 DynamoDB는 NoSQL 데이터베이스입니다."
    }
  ]
}
```

---

## 20. ECS Task Role 권한

S3와 DynamoDB 권한은 `task execution role`이 아니라 `task role`에 추가해야 한다.

```text
Task execution role:
  ECS가 ECR image pull, CloudWatch Logs 전송에 사용

Task role:
  컨테이너 안의 FastAPI 코드가 AWS API 호출에 사용
```

이번 실습에서는 기존 task role에 S3/DynamoDB 권한을 추가했다.

```text
Task role:
  llm-api-bedrock-task-role
```

---

## 21. IAM Policy - S3 / DynamoDB

아래 policy를 task role에 추가했다.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3PracticeAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::llm-api-artifacts-<ACCOUNT_ID>",
        "arn:aws:s3:::llm-api-artifacts-<ACCOUNT_ID>/*"
      ]
    },
    {
      "Sid": "AllowDynamoDBPracticeAccess",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:DescribeTable"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:<ACCOUNT_ID>:table/llm-chat-history"
      ]
    }
  ]
}
```

주의:

```text
<ACCOUNT_ID>는 실제 AWS Account ID로 바꿔야 한다.
```

---

## 22. ECS 환경변수 추가

Task Definition 새 revision에 아래 환경변수를 추가했다.

```text
S3_BUCKET=llm-api-artifacts-<ACCOUNT_ID>
DDB_TABLE=llm-chat-history
```

기존 환경변수도 유지했다.

```text
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=<실제_MODEL_ID>
USE_BEDROCK=true
```

---

## 23. ECR push

S3/DynamoDB 코드 추가 후 Docker image를 다시 build했다.

```powershell
docker build -t llm-api:local .
```

ECR tag:

```powershell
docker tag llm-api:local "${ECR_URI}:s3-ddb-v1"
docker tag llm-api:local "${ECR_URI}:latest"
```

Push:

```powershell
docker push "${ECR_URI}:s3-ddb-v1"
docker push "${ECR_URI}:latest"
```

---

## 24. ECS 재배포

Task Definition 새 revision 생성:

```text
Image:
  <ECR_URI>:s3-ddb-v1

Task role:
  S3 / DynamoDB / Bedrock 권한이 있는 task role

Environment variables:
  S3_BUCKET
  DDB_TABLE
```

Service update:

```text
ECS
  → llm-api-service
  → Update
  → 새 task definition revision 선택
  → Force new deployment
```

---

## 25. ALB 테스트

### S3 저장

```powershell
curl.exe -X POST http://ALB-DNS-NAME/storage/s3/text -H "Content-Type: application/json" --data-binary "@request-s3-put.json"
```

### S3 조회

```powershell
curl.exe http://ALB-DNS-NAME/storage/s3/text/notes/day5/s3-fastapi-test.txt
```

### DynamoDB 저장

```powershell
curl.exe -X POST http://ALB-DNS-NAME/history -H "Content-Type: application/json" --data-binary "@request-history-put.json"
```

### DynamoDB 조회

```powershell
curl.exe http://ALB-DNS-NAME/history/session-fastapi-test
```

---

## 26. 성공 기준

최소 성공:

```text
[ ] S3 bucket 생성
[ ] CLI로 S3 put/get 성공
[ ] DynamoDB table 생성
[ ] CLI로 DynamoDB put/query 성공
```

목표 성공:

```text
[ ] scripts/test_s3.py 성공
[ ] scripts/test_dynamodb.py 성공
[ ] 로컬 FastAPI S3 endpoint 성공
[ ] 로컬 FastAPI DynamoDB endpoint 성공
```

최고 성공:

```text
[ ] ECS task role에 S3/DynamoDB 권한 추가
[ ] ECR에 s3-ddb-v1 push
[ ] ECS 새 revision 배포
[ ] ALB에서 S3 endpoint 성공
[ ] ALB에서 DynamoDB endpoint 성공
```

---

## 27. 오늘 배운 핵심

```text
S3는 파일/object 저장소다.
DynamoDB는 NoSQL 데이터베이스다.
S3 object는 bucket + key로 식별한다.
DynamoDB item은 primary key로 식별한다.
DynamoDB에서 session 단위 이력을 저장하려면 session_id를 partition key로 사용할 수 있다.
created_at을 sort key로 두면 시간순 이력 조회에 유리하다.
ECS에서 S3/DynamoDB를 호출하려면 task role에 권한을 추가해야 한다.
```