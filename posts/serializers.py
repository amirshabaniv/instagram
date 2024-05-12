from .models import Post, File, SavePost, Comment, Like

from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()


class FileSerialzer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ['id', 'file', 'post']


class FileForSavePostSerialzer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = ['id', 'file']


class CreatePostSerializer(serializers.ModelSerializer):
    files = FileSerialzer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'files']


class PostSerializer(serializers.ModelSerializer):
    files = FileSerialzer(many=True)
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'files', 'likes', 'created_at']

    def get_likes(self, obj):
        return obj.plikes.all().count()


class PostForUserSerializer(serializers.ModelSerializer):
    files = FileSerialzer(many=True)

    class Meta:
        model = Post
        fields = ['id','files']


class SavePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = SavePost
        fields = ['id', 'user', 'post']


class ListSavePostsSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = SavePost
        fields = ['id', 'file']

    def get_file(self, obj):
        file = obj.post.files.all().order_by('created_at').first()
        srz = FileForSavePostSerialzer(file)
        return srz.data


class UserForCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'image']


class ReplySerializer(serializers.ModelSerializer):
    user = UserForCommentSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    user = UserForCommentSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'body', 'created_at']


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']


class UserForLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'image']


class PostForExploreSerializer(serializers.ModelSerializer):
    files = FileSerialzer(many=True)

    class Meta:
        model = Post
        fields = ['id','files']
