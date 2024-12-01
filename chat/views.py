from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse as response   
from rest_framework.decorators import api_view
from rest_framework.response import Response
 
from .models import Message 
def index(request):
    return render(request, "chat/index.html")

@csrf_exempt
def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})


@csrf_exempt
def rooms(request, room_name):
    if request.method == "POST":
        text_data = request.body.decode("utf-8")
        print(text_data)

        text_data = json.loads(text_data)
        print(text_data)
        message = text_data["message"]
        sender = text_data["sender"]
        return response({"room_name": room_name,"sender":sender,"message":message})
    
# @api_view(['GET'])
# def get_message(request):
#     message = Message.objects.all()
#     serializer = Message_serializer(message, many=True)
#     return Response(serializer.data)