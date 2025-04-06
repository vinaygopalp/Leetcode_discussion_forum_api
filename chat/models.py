from django.db import models
class User(models.Model):
    user_name = models.CharField(max_length=255, unique=True)
class ChatRoom(models.Model):
   
    created_at = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=255, unique=True)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_name = models.ForeignKey(User,on_delete=models.CASCADE, related_name="messages")
from django.db import models

class ScheduledContest(models.Model):
    contest_id = models.CharField(max_length=255, unique=True)
    template_id = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    problems_id = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contest_id} ({self.start_datetime} to {self.end_datetime})"
