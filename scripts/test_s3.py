import os
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv


load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")
bucket = os.getenv("S3_BUCKET")

if not bucket:
    raise RuntimeError("S3_BUCKET is not set")

s3 = boto3.client("s3", region_name=region)

now = datetime.now(timezone.utc).isoformat()
key = f"test/{now}.txt"
body = f"hello from boto3 s3 at {now}"

s3.put_object(
    Bucket=bucket,
    Key=key,
    Body=body.encode("utf-8"),
    ContentType="text/plain; charset=utf-8",
)

response = s3.get_object(
    Bucket=bucket,
    Key=key,
)

content = response["Body"].read().decode("utf-8")

print("bucket:", bucket)
print("key:", key)
print("content:", content)