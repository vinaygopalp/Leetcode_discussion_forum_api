from django.db import models
class User_base(models.Model):
    user_name = models.CharField(max_length=255, unique=True)
    role=models.CharField(max_length=255,default="staff")

class ChatRoom(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=255, unique=True)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_name = models.ForeignKey(User_base,on_delete=models.CASCADE, related_name="messages")

class contest_template(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField(default="2021-01-01")
    end_date = models.DateField(default="9999-12-31")
    start_time = models.TimeField(default="00:00:00")
    end_time = models.TimeField(default="23:59:59")

    problems_id = models.CharField( max_length=50,default="-1")