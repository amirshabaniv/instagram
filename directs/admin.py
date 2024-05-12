from django.contrib import admin
from .models import Message


class MessageAdmin(admin.ModelAdmin):
    list_editable = ['message']
    list_display = ['user', 'sender', 'reciever', 'message']

admin.site.register(Message, MessageAdmin)