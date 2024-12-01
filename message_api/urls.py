from django.urls import path

from . import views
from rest_framework import routers, serializers, viewsets
from .models import *
# Serializers define the API representation.

 
urlpatterns = [
    path("message/", views.get_message, name="get_message"),
    path("room/", views.add_room, name="add_room"),
    path("user/", views.add_user, name="add_user"),
# 
]