# AWS 실습 명령어 모음

이 문서는 AWS 계정 사용 가능일에 실행할 명령어를 정리한 것이다.

현재 목표:

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

---

## 1. 계정 확인

```powershell
aws --version
aws sts get-caller-identity
```

`aws sts get-caller-identity`가 성공하면 현재 인증된 AWS 계정 정보를 확인할 수 있다.

예상 형태:

```json
{
  "UserId": "...",
  "Account": "123456789012",
  "Arn": "..."
}
```

---

## 2. 변수 설정

```powershell
$REGION="ap-northeast-2"
$APP_NAME="llm-api"
$ACCOUNT_ID = (aws sts get-caller-identity | ConvertFrom-Json).Account
$ECR_URI = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$APP_NAME"
```

확인:

```powershell
$ACCOUNT_ID
$ECR_URI
```

예상 ECR URI:

```text
123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/llm-api
```

---

## 3. ECR repository 생성

```powershell
aws ecr create-repository `
  --repository-name $APP_NAME `
  --region $REGION
```

이미 repository가 있으면 에러가 날 수 있다.
그 경우 다음 단계로 진행한다.

확인:

```powershell
aws ecr describe-repositories `
  --repository-names $APP_NAME `
  --region $REGION
```

---

## 4. ECR 로그인

```powershell
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
```

성공 메시지:

```text
Login Succeeded
```

---

## 5. Docker image tag

```powershell
docker tag llm-api:local "$ECR_URI:latest"
```

확인:

```powershell
docker images
```

---

## 6. ECR push

```powershell
docker push "$ECR_URI:latest"
```

확인:

```powershell
aws ecr describe-images `
  --repository-name $APP_NAME `
  --region $REGION
```

---

## 7. 최종 확인

ECR에 image가 올라가면 ECS Task Definition에서 아래 image URI를 사용한다.

```text
$ECR_URI:latest
```
