from django.urls import path

from . import views
from .models import *
# Serializers define the API representation.

 
urlpatterns = [
    path("message/", views.get_message, name="get_message"),
    path("room/", views.add_room, name="add_room"),
    path("user/", views.add_user, name="add_user"),
    path("comp/", views.compexlity_analysis, name="openai"),
    path("rabbitmq/sorted_publish", views.sorted_publish, name="rabbitmq"),
    path("rabbitmq/sorted_consume", views.sorted_consumer, name="rabbitmq_consume"),
    path("rabbitmq/template_publish", views.template_publish, name="template_publish"),
    path("rabbitmq/template_consume", views.template_consumer, name="template_consumer"),
    path("rabbitmq/ack", views.ack, name="ack"),
    path("contest_template/", views.contest_template, name="contest_template"),
# 
]