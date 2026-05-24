import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3

from app.core.config import settings


class ChatHistoryService:
    def __init__(self) -> None:
        if not settings.ddb_table:
            raise RuntimeError("DDB_TABLE is not set")

        dynamodb = boto3.resource(
            "dynamodb",
            region_name=settings.aws_region,
        )
        self.table = dynamodb.Table(settings.ddb_table)

    async def put_history(
        self,
        session_id: str,
        message: str,
        answer: str,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(
            self._put_history_sync,
            session_id,
            message,
            answer,
        )

    def _put_history_sync(
        self,
        session_id: str,
        message: str,
        answer: str,
    ) -> dict[str, Any]:
        item = {
            "session_id": session_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chat_id": str(uuid.uuid4()),
            "message": message,
            "answer": answer,
        }

        self.table.put_item(Item=item)

        return item

    async def list_history(self, session_id: str) -> list[dict[str, Any]]:
        return await asyncio.to_thread(
            self._list_history_sync,
            session_id,
        )

    def _list_history_sync(self, session_id: str) -> list[dict[str, Any]]:
        response = self.table.query(
            KeyConditionExpression="session_id = :sid",
            ExpressionAttributeValues={
                ":sid": session_id,
            },
        )

        return response.get("Items", [])


chat_history_service = ChatHistoryService()