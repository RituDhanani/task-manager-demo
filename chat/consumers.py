import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.services import create_message, user_can_join_room


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_room_{self.room_id}"

        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        allowed = await self.has_room_access()
        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data):
      
        data = json.loads(text_data)
        message_text = data.get("message")

        if not message_text:
            return

        message = await self.save_message(message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message.content,
                "sender": self.user.username,
                "timestamp": message.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        """
        Receive chat message from group.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "CHAT_MESSAGE",
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def task_status(self, event):
        """
        Receive task status update broadcast.
        """
        await self.send(
            text_data=json.dumps(
                {
                    "type": "TASK_STATUS_UPDATE",
                    "task_id": event["task_id"],
                    "status": event["status"],
                }
            )
        )


    @database_sync_to_async
    def has_room_access(self) -> bool:
        return user_can_join_room(
            user=self.user,
            room_id=self.room_id,
        )

    @database_sync_to_async
    def save_message(self, content):
        return create_message(
            room_id=self.room_id,
            user_id=self.user.id,
            content=content,
        )