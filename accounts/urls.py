from unicodedata import name
from django.urls import path, include
from .views import (
        RegisterView, 
        VerifyUserEmail,
        LoginUserView, 
        PasswordResetConfirm, 
        PasswordResetRequestView,SetNewPasswordView, LogoutApiView,
        UserAPIView, FollowAPIView, FollowRequestResponseAPIView, UnfollowAPIView,
        FollowersAPIView, FollowingsAPIView, RemoveFollowerAPIView,
        CreateStoryAPIView, StoryAPIView, StoryViewersAPIView, RemoveStoryAPIView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('logout/', LogoutApiView.as_view(), name='logout'),

    path('follow/<int:user_id>/', FollowAPIView.as_view(), name='follow'),
    path('follow-requests/', FollowRequestResponseAPIView.as_view(), name='follow-requests'),
    path('follow-request-response/<int:follow_request_id>/', FollowRequestResponseAPIView.as_view(), name='follow-request-response'),
    path('unfollow/<int:user_id>/', UnfollowAPIView.as_view(), name='unfollow'),
    path('followers/<str:username>/', FollowersAPIView.as_view(), name='followers'),
    path('followings/<str:username>/', FollowingsAPIView.as_view(), name='followings'),
    path('remove-follow/<int:user_id>/', RemoveFollowerAPIView.as_view(), name='remove'),

    path('users/<str:username>/', UserAPIView.as_view(), name='user'),

    path('create-story/', CreateStoryAPIView.as_view(), name='create-story'),
    path('story/<int:user_id>/<int:story_id>/', StoryAPIView.as_view(), name='see-story'),
    path('story-viewers/<int:story_id>/', StoryViewersAPIView.as_view(), name='story-viewers'),
    path('remove-story/<int:story_id>/', RemoveStoryAPIView.as_view(), name='remove-story'),
]
