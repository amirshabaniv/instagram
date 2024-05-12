from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    reciever_user = UserSerializer(read_only=True)
    sender_user = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id','sender', 'reciever', 'sender_user', 'reciever_user', 'message', 'file', 'is_read', 'created_at']