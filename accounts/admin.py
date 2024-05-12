from django.contrib import admin
from .models import OneTimePassword, Follow, FollowRequest, Story, StoryView
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.register(User)

admin.site.register(OneTimePassword)

admin.site.register(Follow)

admin.site.register(FollowRequest)

admin.site.register(Story)

admin.site.register(StoryView)