from django.contrib import admin

from .models import *
admin.site.register(Message)
admin.site.register(ChatRoom)
admin.site.register(User_base)

# Register your models here.
