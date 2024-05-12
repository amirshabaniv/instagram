from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
import os

from .managers import UserManager
from config.timestamp import TimeStamp 


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('Female', 'Female'),
        ('Male', 'Male'),
        ('Custom', 'Custom'),
        ('Prefer not to say', 'Prefer not to say')
    )

    id = models.BigAutoField(primary_key=True, editable=False) 
    email = models.EmailField(
        max_length=255, verbose_name=_("Email Address"), unique=True
    )
    username = models.CharField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified=models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=False)
    name = models.CharField(max_length=100, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, null=True, blank=True)
    bio = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to='media/profiles_images', null=True, blank=True)

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }

    def __str__(self):
        return self.email


class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)

    def __str__(self):
        return f"{self.user.username} - otp code"


class FollowRequest(TimeStamp):
    class FollowRequestStatus(models.TextChoices):
        Requesting = 'Requesting', 'Requesting'
        ACCEPT = 'Accept', 'Accept'
        REJECT = 'Reject', 'Reject'
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings_request')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_request')
    status = models.CharField(max_length=20, choices=FollowRequestStatus.choices)

    def follow_request(self):
        self.status = FollowRequest.FollowRequestStatus.Requesting
        self.save()

    def response_to_follow_request(self, response):
        if response == 'Accept':
            self._accept_follower()
        elif response == 'Requesting':
            self._reject_follower()

    def _accept_follower(self):
        self.status = FollowRequest.FollowRequestStatus.ACCEPT
        self.save()

    def _reject_follower(self):
        self.status = FollowRequest.FollowRequestStatus.REJECT
        self.save()
    
    def __str__(self):
        return f'{self.from_user.username} sent follow request to {self.to_user.username}'


class Follow(TimeStamp):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')

    def __str__(self):
        return f'{self.from_user.username} followed {self.to_user.username}'
    

class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    file = models.FileField(upload_to='media/story_files')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'

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
        return f'{self.user.username} created a story'
        

class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'viewer')

    def __str__(self):
        return f'{self.viewer.username} seen a story from {self.story.user.username}'
