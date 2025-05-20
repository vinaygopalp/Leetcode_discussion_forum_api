from django.urls import path

from . import views
from rest_framework import routers, serializers, viewsets
from chat.models import *
# Serializers define the API representation.
class User_serializer(serializers.ModelSerializer):
    class Meta:
        model = Users
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
 

class template_contest_ser(serializers.Serializer):
   
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    tags=serializers.ListField()
    prize=serializers.ListField()


class admin_contest_Ser(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    problems_id = serializers.ListField()



import time
from datetime import timezone

# Helper to convert datetime to UNIX timestamp
def to_unix(dt):
    if dt:
        return int(time.mktime(dt.timetuple()))
    return None

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = '__all__'


class ScheduledContestSerializer(serializers.ModelSerializer):
    start_unix = serializers.SerializerMethodField()
    end_unix = serializers.SerializerMethodField()

    class Meta:
        model = ScheduledContest
        fields = ['contest_id', 'template_id', 'start_datetime', 'end_datetime', 'created_at', 'problems_id', 'start_unix', 'end_unix']

    def get_start_unix(self, obj):
        return to_unix(obj.start_datetime)

    def get_end_unix(self, obj):
        return to_unix(obj.end_datetime)


class ContestParticipantSerializer(serializers.ModelSerializer):
    user = User_serializer()
    contest = ScheduledContestSerializer()
    entered_unix = serializers.SerializerMethodField()

    class Meta:
        model = Contest_Particpants
        fields = ['user', 'contest', 'entered_time', 'active', 'entered_unix']

    def get_entered_unix(self, obj):
        return to_unix(obj.entered_time)


class ContestLeaderboardSerializer(serializers.ModelSerializer):
    contest_participant = ContestParticipantSerializer()
    updated_unix = serializers.SerializerMethodField()

    class Meta:
        model = Contest_Leaderboard
        fields = ['contest_participant', 'total_solved_problem', 'reward_points', 'updated_time', 'updated_unix']

    def get_updated_unix(self, obj):
        return to_unix(obj.updated_time)