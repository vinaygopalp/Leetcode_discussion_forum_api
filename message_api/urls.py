from django.urls import path

from . import views
from .models import *
# Serializers define the API representation.

 
urlpatterns = [
    path("message/", views.get_message, name="get_message"),
    path("room/", views.add_room, name="add_room"),
    path("user/", views.add_user, name="add_user"),
    path("comp/", views.compexlity_analysis, name="openai"),
    path("rabbitmq/temp_publish", views.temp_publish, name="rabbitmq"),
    path("rabbitmq/temp_consume", views.temp_consumer, name="rabbitmq_consume"),
    #path("rabbitmq/sorted_publish", views.sorted_publish, name="template_publish"),
    path("rabbitmq/sorted_consume", views.sorted_consumer, name="template_consumer"),
    path("rabbitmq/ack", views.ack, name="ack"),
    path("contest_template/", views.contest_template, name="contest_template"),
    path("contest_start/", views.contest_start, name="contest_start"),
# 
]