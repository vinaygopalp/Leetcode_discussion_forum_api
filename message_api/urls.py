from django.urls import path

from . import views
from .models import *
# Serializers define the API representation.

 
urlpatterns = [
    path("message/<str:room_name>", views.get_message, name="get_message"),
    path("room/", views.add_room, name="add_room"),
    path("user/", views.add_user, name="add_user"),
    path("comp/", views.compexlity_analysis, name="openai"),
    # path("rabbitmq/temp_publish", views.temp_publish, name="rabbitmq"),
    #path("rabbitmq/sorted_publish", views.sorted_publish, name="template_publish"),
    #path("rabbitmq/sorted_consume", views.sorted_consumer, name="template_consumer"),
    #path("rabbitmq/ack", views.ack, name="ack"),
    path("contest_template/", views.contest_template, name="contest_template"),
    path("contest_start/", views.contest_start, name="contest_start"),
    path("schedule_contest/", views.schedule_contest_view, name="schedule_contest"),
    path("all_templates/",views.list_templates, name="list_templates"),
    path("all_schedules/",views.view_all_scheduled_contests, name="all_sch"),
     path('delete_all_contests/', views.delete_all_contests,name="delete_all_contests"),
    path('delete_all_templates/', views.delete_all_templates,name="delete_all_templates"),
    path('test/', views.test, name="test"),
    path('contest_registration/', views.contest_registration, name="contest_registration"),
   path("leaderboard/", views.get_leaderboard, name="rabbitmq_consume"),
   path("consumer/",views.start_consuming, name="consumer"),
     
# 
]