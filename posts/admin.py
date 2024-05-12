from django.contrib import admin

from .models import Post, File, SavePost, Comment, Like


admin.site.register(Post)

admin.site.register(File)

admin.site.register(SavePost)

admin.site.register(Comment)

admin.site.register(Like)