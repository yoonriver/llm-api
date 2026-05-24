import os

import boto3
from dotenv import load_dotenv


load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")
model_id = os.getenv("BEDROCK_MODEL_ID")

if not model_id:
    raise RuntimeError("BEDROCK_MODEL_ID is not set")

client = boto3.client("bedrock-runtime", region_name=region)

response = client.converse(
    modelId=model_id,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "한국어로 짧게 자기소개해줘."
                }
            ],
        }
    ],
    inferenceConfig={
        "maxTokens": 300,
        "temperature": 0.7,
    },
)

print(response["output"]["message"]["content"][0]["text"])