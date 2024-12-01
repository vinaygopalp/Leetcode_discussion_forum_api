from django.urls import path

from . import views
from rest_framework import routers, serializers, viewsets
from chat.models import *
# Serializers define the API representation.
class User_serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
class ChatRoom_serializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'
class Message_serializer(serializers.ModelSerializer):
    user_name =User_serializer()  # This will serialize the related User
    room = ChatRoom_serializer()
    class Meta:
        model = Message
        fields = '__all__'
        depth = 1
 
 