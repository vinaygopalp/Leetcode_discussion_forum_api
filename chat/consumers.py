import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Message, ChatRoom,Users, Contest_Leaderboard 
from channels.db import database_sync_to_async
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
    def my_database_operation(self, message, sender):
        try:
            room = ChatRoom.objects.get(room=self.room_name)
            senderr = Users.objects.get(username=sender)
            print(room,senderr)  # Fixed attribute
            Message.objects.create(content=message, room=room, user_name=senderr)
        except ChatRoom.DoesNotExist:
            return "Room does not exist"
        except Users.DoesNotExist:
            return "User does not exist"
        return None

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            sender = text_data_json["sender"]
        except (ValueError, KeyError):
            await self.close(1000)  # Correct way to close connection
            return
        
        error = await self.my_database_operation(message, sender)
        if error:
            await self.send(text_data=json.dumps({"error": error}))
            await self.close(1000)
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
        }))
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.contest_id = self.scope["url_route"]["kwargs"]["contest_id"]
        self.room_group_name = f"leaderboard_{self.contest_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        leaderboard_data = text_data_json["message"]
        sender = text_data_json.get("sender", "system")

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "leaderboard_message",
                "message": leaderboard_data,
                "sender": "system",
            }
        )

    async def leaderboard_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": "system",
        }))


async def send_leaderboard_data(self, event):
    message = event["message"]
    await self.send(text_data=json.dumps({
        "message": message
    }))
