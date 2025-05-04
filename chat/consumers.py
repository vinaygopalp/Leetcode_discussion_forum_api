# # import json
# # from channels.generic.websocket import AsyncWebsocketConsumer
# # from chat.models import Message, ChatRoom
# # from channels.db import database_sync_to_async
# # from django.contrib.auth.models import User

# # class ChatConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
# #         self.room_group_name = f"chat_{self.room_name}"
# #         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
# #         await self.accept()

# #     async def disconnect(self, close_code):
# #         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

# #     # @database_sync_to_async
# #     # def my_database_operation(self, encrypted_message, sender):
# #     #     room = ChatRoom.objects.get(code=self.room_name, name=sender)
# #     #     senderr = User.objects.get(username=sender)
# #     #     Message.objects.create(content=encrypted_message, room=room, user=senderr)

# #     async def receive(self, text_data):
# #         text_data_json = json.loads(text_data)
# #         message = text_data_json["message"]
# #         print("message:", message)
# #         sender = text_data_json["sender"]

# #         await self.my_database_operation(message, sender)

# #         await self.channel_layer.group_send(
# #             self.room_group_name,
# #             {
# #                 "type": "chat_message",
# #                 "message": message,
# #                 "sender": sender,
# #             }
# #         )

# #     async def chat_message(self, event):
# #         message = event["message"]
# #         sender = event["sender"]

# #         await self.send(text_data=json.dumps({
# #             "message": message,
# #             "sender": sender,
# #         }))
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from chat.models import Message, ChatRoom, User
# from channels.db import database_sync_to_async
# from rest_framework.response import Response
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group (no need to use async_to_sync)
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     @database_sync_to_async
#     def my_database_operation(self, message, sender):
#         try:
#             room = ChatRoom.objects.get(room=self.room_name)
#             senderr = User.objects.get(user_name=sender)
#             Message.objects.create(content=message, room=room, user_name=senderr)
#         except ChatRoom.DoesNotExist:
#             ChatConsumer.disconnect(self, 1000)
#             return Response({"error": "Room does not exist"})
#         except User.DoesNotExist:
#             ChatConsumer.disconnect(self, 1000)
#             return Response({"error": "User does not exist"})

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
#             message = text_data_json["message"]
#             sender = text_data_json["sender"]

#         except ValueError:
#             ChatConsumer.disconnect(self, 1000)
#             return Response({"error": "Invalid JSON"})
#         except KeyError:
#             return Response({"error": "Invalid JSON"})
#         except:  
#             return Response({"error": "Invalid JSON"})   
#         await self.my_database_operation(message, sender)

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "message": message,
#                 "sender": sender,
#             }
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]
#         sender = event["sender"]

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             "message": message,
#             "sender": sender,
#         }))
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Message, ChatRoom,Users
 
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