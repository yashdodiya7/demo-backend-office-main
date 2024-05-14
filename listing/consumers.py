# consumers.py

import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


def send_notification_to_users(listing_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"listing_{listing_id}",
        {"type": "send_notification", "message": "New interest created"}
    )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        await self.channel_layer.group_add(
            f"user_{self.user_id}",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            f"user_{self.user_id}",
            self.channel_name
        )

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
