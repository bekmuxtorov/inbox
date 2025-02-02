import json
from datetime import datetime as dt

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Ticket, Message, UserDetails
from django.contrib.auth.models import User
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.ticket_id = self.scope["url_route"]["kwargs"]["ticket_uuid"]
        self.ticket_group_name = f"chat_{self.ticket_id}"

        ticket, _ = await Ticket.objects.aget_or_create(ticket_uuid=self.ticket_id)
        self.ticket = ticket

        await self.channel_layer.group_add(self.ticket_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.ticket_group_name, self.channel_name)
        await self.set_user_offline()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json.get("message", "").strip()
        time = text_data_json.get("time", "")

        if not message_text:
            return

        await self.save_message(message_text)

        await self.channel_layer.group_send(
            self.ticket_group_name,
            {
                "type": "chat.message",
                "message": message_text,
                "user": await self.get_user_details(),
                "time": time
            },
        )

    @database_sync_to_async
    def set_user_offline(self):
        user = UserDetails.objects.filter(id=self.scope["user"].id).first()
        if user:
            user.status = "offline"
            user.save()

    @database_sync_to_async
    def get_user(self):
        return self.scope["user"]

    @database_sync_to_async
    def get_user_details(self):
        return self.ticket.user_details

    async def save_message(self, message_text):
        user = await self.get_user()

        await Message.objects.acreate(
            sender_operator=user if isinstance(user, User) else None,
            sender_guest=await self.get_user_details() if not isinstance(user, User) else None,
            ticket=self.ticket,
            text=message_text,
        )

    async def chat_message(self, event):
        user = event["user"]
        await self.send(text_data=json.dumps({"message": event["message"], "sender": user.username, "time": event["time"]}))
