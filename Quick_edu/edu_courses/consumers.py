import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


# for enrollmet notification
class EnrollmentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
            self.room_group_name = 'course_enrollment'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'enrollment_alert',
                'username': username,
                'message': message
            }
        )
    async def enrollment_alert(self, event):
        message = event['message']
        username = event['username']
        # Send the message to the user (e.g., display it in a notification)
        await self.send(text_data=json.dumps({
            'type': 'enrollment_alert',
            'username': username,
            'message': message
        }))


# for course notification
class CourseNotificationConsumer(AsyncWebsocketConsumer):
        async def connect(self):
            user = self.scope['user']
            if user.is_authenticated:
                await self.channel_layer.group_add('course_updates',self.channel_name)
                await self.accept()
        async def disconnect(self, close_code):
            user = self.scope['user']
            if user.is_authenticated:
                await self.channel_layer.group_discard('course_updates',self.channel_name)
        async def send_notification(self, event):
            message = event['message']
            await self.send(text_data=json.dumps({
                'message': message
            }))
        @classmethod
        def send_newcourse_notification(cls, message):
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                    "course_updates",
                {
                    "type": "send_notification",
                    'message': message,
                }
            )

