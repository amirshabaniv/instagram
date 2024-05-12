from django.urls import path
from . import views


urlpatterns = [
    path('send-messages/', views.SendMessagesAPIView.as_view(), name='send-messages'),
    path('recieve-messages/<sender_id>/<reciever_id>/', views.RecieveMessagesAPIView.as_view(), name='get-messages'),
    path('my-directs/<user_id>/', views.MyDirectsAPIView.as_view(), name='my-inbox'),
    path('search/user/<str:username>/', views.SearchUserAPIView.as_view(), name='search-user'),
]