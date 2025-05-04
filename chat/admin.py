from django.contrib import admin

from .models import Message, ChatRoom, Users
admin.site.register(Message)
admin.site.register(ChatRoom)
admin.site.register(Users)

# Register your models here.
