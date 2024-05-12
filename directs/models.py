from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user")
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sender")
    reciever = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reciever")
    message = models.CharField(max_length=20000)
    file = models.FileField(upload_to='media/chat_files', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender} send message to {self.reciever}'