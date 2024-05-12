from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
import os

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.user.username} created a post'
    

class File(models.Model):
    file = models.FileField(upload_to='media/posts_files')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def file_type(self):
        video_formats = ('.mp4', '.mkv', '.avi')
        image_formats = ('.jpg', '.jpeg', '.png')
        name, extension = os.path.splitext(self.file.name)
        if extension.lower() in video_formats:
            return 'video'
        elif extension.lower() in image_formats:
            return 'image'
        else:
            return 'unacceptable'

    def __str__(self):
        return f"This file is for {self.post.user.username}'s post"


class SavePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_save_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_save_posts')

    def __str__(self):
        return f'{self.user.username} saved the post:{self.post.caption[:10]}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ucomments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='pcomments')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, related_name='rcomments', blank=True, null=True)
    is_reply = models.BooleanField(default=False)
    body = models.TextField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.body[:30]}'
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ulikes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='plikes')

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user.username} liked {self.post.caption[:10]}'