from django.db import models
from django.contrib.postgres.fields import ArrayField
# class User_base(models.Model):
#     user_name = models.CharField(max_length=255, unique=True)
#     role=models.CharField(max_length=255,default="staff")

class Problem(models.Model):
    id = models.BigIntegerField(primary_key=True)
    rating = models.BigIntegerField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    difficulty = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'problem'


class Users(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    email = models.TextField(unique=True, blank=True, null=True)
    password = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
        
class ChatRoom(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    room = models.CharField(max_length=255, unique=True)

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user_name = models.ForeignKey(Users,on_delete=models.CASCADE, related_name="messages")

class ScheduledContest(models.Model):
    contest_id = models.CharField(max_length=255, unique=True)
    template_id = models.CharField(max_length=255)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    problems_id = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def problems(self):
        return Problem.objects.filter(id__in=self.problems_id)
    
    def __str__(self):
        return f"{self.contest_id} ({self.start_datetime} to {self.end_datetime})"

 

class Contest_Particpants(models.Model):  
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="contest_participant")
    contest = models.ForeignKey(ScheduledContest, on_delete=models.CASCADE , related_name="contest")
    entered_time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    class Meta:
        unique_together = ('user_id', 'contest_id')
    def __str__(self):
        return f"{self.user.username} - {self.contest.contest_id}"
    
class Contest_Leaderboard(models.Model):
    contest_participant = models.ForeignKey(Contest_Particpants, on_delete=models.CASCADE, related_name="contest_participant")
    total_solved_problem = models.JSONField()
    reward_points = models.BigIntegerField()
    updated_time = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.contest_participant.user.username} in {self.contest_participant.contest.contest_id}"