import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.services import create_message, user_can_join_room
from chat.models import ChatRoom


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_room_{self.room_id}"

        # 1️⃣ Reject unauthenticated users
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        # 2️⃣ Check role-based access
        allowed = await self.has_room_access()
        if not allowed:
            await self.close()
            return

        # 3️⃣ Join Redis group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()


    @database_sync_to_async
    def has_room_access(self) -> bool:
        return user_can_join_room(
            user=self.user,
            room_id=self.room_id,
        )