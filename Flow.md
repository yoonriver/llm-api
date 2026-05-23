[내 PC]
Docker image: llm-api:local
  ↓ docker tag
ECR 주소가 붙은 image
  ↓ docker push

[AWS]
Amazon ECR
  ↓ ECS가 image pull

ECS Fargate
  ↓ FastAPI container 실행

ALB
  ↓ 외부 요청 전달

GET /health
POST /chat mock