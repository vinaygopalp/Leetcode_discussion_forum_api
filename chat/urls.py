from django.urls import path

from . import views
from rest_framework import routers, serializers, viewsets
from .models import *
# Serializers define the API representation.

 
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
   path("rooms/<str:room_name>/", views.rooms, name="rooms"),
#    path("get_message/", views.get_message, name="get_message"),
# 
]