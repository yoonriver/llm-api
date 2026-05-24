import os
import uuid
from datetime import datetime, timezone

import boto3
from dotenv import load_dotenv


load_dotenv()

region = os.getenv("AWS_REGION", "us-east-1")
table_name = os.getenv("DDB_TABLE")

if not table_name:
    raise RuntimeError("DDB_TABLE is not set")

dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table(table_name)

session_id = "session-script-test"
created_at = datetime.now(timezone.utc).isoformat()
chat_id = str(uuid.uuid4())

item = {
    "session_id": session_id,
    "created_at": created_at,
    "chat_id": chat_id,
    "message": "DynamoDB script test",
    "answer": "Saved successfully",
}

table.put_item(Item=item)

response = table.query(
    KeyConditionExpression="session_id = :sid",
    ExpressionAttributeValues={
        ":sid": session_id,
    },
)

print("table:", table_name)
print("inserted:", item)
print("items:", response["Items"])