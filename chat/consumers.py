import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.services import create_message
from chat.models import ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Async WebSocket consumer for group chat.
    """
    async def connect(self):
        self.user = self.scope["user"]

        # URL param: /ws/chat/<room_id>/
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_room_{self.room_id}"

        # Reject unauthenticated users (JWT later)
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        # Validate room exists (async safe)
        room_exists = await self.room_exists(self.room_id)
        if not room_exists:
            await self.close()
            return

        # Join group
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
        """
        Receive message from WebSocket
        """
        data = json.loads(text_data)
        message_text = data.get("message")

        if not message_text:
            return

        message = await self.save_message(message_text)

        # Broadcast message to group
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
        Receive message from group
        """
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender": event["sender"],
                    "timestamp": event["timestamp"],
                }
            )
        )


    @database_sync_to_async
    def room_exists(self, room_id):
        return ChatRoom.objects.filter(id=room_id, is_active=True).exists()

    @database_sync_to_async
    def save_message(self, content):
        return create_message(
            room_id=self.room_id,
            user_id=self.user.id,
            content=content,
        )