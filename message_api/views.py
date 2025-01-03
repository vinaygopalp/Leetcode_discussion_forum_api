from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import Message_serializer,ChatRoom_serializer,User_serializer
from chat.models import Message,ChatRoom,User
# Create your views here.
@api_view(['GET', 'POST','DELETE'])
def get_message(request):
    if request.method == "GET":
        messages = Message.objects.all()
        serializer = Message_serializer(messages, many=True) 
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = Message_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        message = Message.objects.get(id=request.data["id"])
        message.delete()
        return Response({"message":"Message Deleted"})
    

@api_view(['GET','POST','DELETE'])
def add_room(request):
    if request.method == "GET":
        rooms = ChatRoom.objects.all()
        serializer = ChatRoom_serializer(rooms, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ChatRoom_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        room = ChatRoom.objects.get(id=request.data["id"])
        room.delete()
        return Response({"message":"Room Deleted"})

@api_view(['GET','POST','DELETE'])
def add_user(request):
    if request.method == "GET":
        users = User.objects.all()
        serializer = User_serializer(users, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = User_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({"errors":serializer.errors})
    elif request.method == "DELETE":
        user = User.objects.get(id=request.data["id"])
        user.delete()
        return Response({"message":"User Deleted"})