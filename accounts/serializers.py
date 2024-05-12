import json
from dataclasses import field
from rest_framework import serializers
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .utils import send_normal_email
from .models import Follow, FollowRequest, Story, StoryView
from posts.serializers import PostForUserSerializer

from django.contrib.auth import get_user_model
User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2= serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model=User
        fields = ['email', 'username', 'password', 'password2']

    def validate(self, attrs):
        password=attrs.get('password', '')
        password2 =attrs.get('password2', '')
        if password !=password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def create(self, validated_data):
        user= User.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),
            password=validated_data.get('password')
            )
        return user


class VerifySerializer(serializers.Serializer):
    otp = serializers.CharField()

    class Meta:
        fields = ['otp']
        

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    access_token=serializers.CharField(max_length=255, read_only=True)
    refresh_token=serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request=self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("invalid credential try again")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        tokens=user.tokens()
        return {
            'email':user.email,
            "access_token":str(tokens.get('access')),
            "refresh_token":str(tokens.get('refresh'))
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user= User.objects.get(email=email)
            uidb64=urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request=self.context.get('request')
            current_site=get_current_site(request).domain
            relative_link =reverse('reset-password-confirm', kwargs={'uidb64':uidb64, 'token':token})
            abslink=f"http://{current_site}{relative_link}"
            print(abslink)
            email_body=f"Hi {user.username} use the link below to reset your password {abslink}"
            data={
                'email_body':email_body, 
                'email_subject':"Reset your Password", 
                'to_email':user.email
                }
            send_normal_email(data)

        return super().validate(attrs)

    
class SetNewPasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password=serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64=serializers.CharField(min_length=1, write_only=True)
    token=serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token=attrs.get('token')
            uidb64=attrs.get('uidb64')
            password=attrs.get('password')
            confirm_password=attrs.get('confirm_password')

            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("reset link is invalid or has expired", 401)
            if password != confirm_password:
                raise AuthenticationFailed("passwords do not match")
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return AuthenticationFailed("link is invalid or has expired")

    
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }
    
    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')


class ForPrivateUserSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'link', 'image', 'followers', 'followings']

    def get_followers(self, obj):
        return Follow.objects.filter(to_user=obj).count()

    def get_followings(self, obj):
        return Follow.objects.filter(from_user=obj).count()
    

class UserSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    followings = serializers.SerializerMethodField()
    posts = PostForUserSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'link', 'gender', 'image', 'followers', 'followings', 'posts']

    def get_followers(self, obj):
        return Follow.objects.filter(to_user=obj).count()

    def get_followings(self, obj):
        return Follow.objects.filter(from_user=obj).count()


class FollowRequestSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(read_only=True, choices=FollowRequest.FollowRequestStatus.choices)

    class Meta:
        model = FollowRequest
        fields = ['id', 'from_user', 'to_user', 'status']


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['id', 'from_user', 'to_user']


class FollowerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['username', 'name', 'image']

    def get_username(self, obj):
        return obj.from_user.username
    
    def get_name(self ,obj):
        return obj.from_user.name
    
    def get_image(self, obj):
        if obj.to_user.image:
            return obj.to_user.image
        return None
    

class FollowingSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ['username', 'name', 'image']

    def get_username(self, obj):
        return obj.to_user.username
    
    def get_name(self, obj):
        return obj.to_user.name
    
    def get_image(self, obj):
        if obj.to_user.image:
            return obj.to_user.image
        return None


class StorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Story
        fields = ['id', 'user', 'file']


class StoryViewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = StoryView
        fields = ['username', 'name', 'image', 'story']

    def get_username(self, obj):
        return obj.viewer.username
    
    def get_name(self ,obj):
        return obj.viewer.name
    
    def get_image(self, obj):
        if obj.viewer.image:
            return obj.viewer.image
        return None


