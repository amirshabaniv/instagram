from django.urls import path, include
from . import views


urlpatterns = [
    path('create-post/', views.CreatePostAPIView.as_view(), name='create-post'),
    path('delete-post/<int:post_id>/', views.DeletePostAPIView.as_view(), name='delete-post'),
    path('posts/<int:user_id>/<int:post_id>/', views.PostAPIView.as_view(), name='posts'),
    path('update-post/<int:post_id>/', views.UpdatePostAPIView.as_view(), name='update-post'),

    path('home/', views.HomeAPIView.as_view(), name='home'),

    path('save-post/<int:post_id>/', views.SavePostAPIView.as_view(), name='save-post'),
    path('delete-save-post/<int:post_id>/', views.DeleteSavePostAPIView.as_view(), name='save-post'),
    path('list-save-posts/', views.ListSavePostsAPIView.as_view(), name='list-save-posts'),
    path('explore/', views.ExploreAPIView.as_view(), name='explore'),

    path('create-comment/<int:post_id>/', views.CreateCommentAPIView.as_view(), name='create-comment'),
    path('delete-comment/<int:pk>/', views.DeleteCommentAPIView.as_view(), name='delete-comment'),
    path('create-reply/<int:post_id>/<int:comment_id>/', views.ReplyCommentAPIView.as_view(), name='create-reply'),
    path('list-comments/<int:user_id>/<int:post_id>/', views.ListCommentsAPIView.as_view(), name='list-comments'),
    path('list-replies/<int:user_id>/<int:comment_id>/', views.ListRepliesAPIView.as_view(), name='list-replies'),

    path('create-like/<int:post_id>/', views.CreateLikeAPIView.as_view(), name='create-like'),
    path('delete-like/<int:pk>/', views.DeleteLikeAPIView.as_view(), name='delete-like'),
    path('list-likes/<int:user_id>/<int:post_id>/', views.ListLikesAPIView.as_view(), name='list-comments'),
]