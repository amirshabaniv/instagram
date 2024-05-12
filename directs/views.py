from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import OuterRef, Subquery
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Message
from .serializers import MessageSerializer
from accounts.serializers import UserSerializer
from permissions import IsAuthenticated, IsOwner2


class SendMessagesAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        srz = self.serializer_class(data=request.data)
        if srz.is_valid():
            srz.save()
            return Response(srz.data, status=status.HTTP_201_CREATED)
        return Response(srz.errors, status=status.HTTP_400_BAD_REQUEST)


class RecieveMessagesAPIView(generics.GenericAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, sender_id, reciever_id):
        if ((request.user.id == sender_id) or (request.user.id == reciever_id)) is not True:
            return Response({'permission denied'}, status=status.HTTP_400_BAD_REQUEST)
        messages =  Message.objects.filter(sender__in=[sender_id, reciever_id], reciever__in=[sender_id, reciever_id])
        srz = self.serializer_class(messages, many=True)
        return Response(srz.data, status=status.HTTP_200_OK)


class DeleteMessageAPIView(generics.DestroyAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]
    

class MyDirectsAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        messages = Message.objects.filter(
            id__in =  Subquery(
                User.objects.filter(
                    Q(sender__reciever=user_id) |
                    Q(reciever__sender=user_id)
                ).distinct().annotate(
                    last_msg=Subquery(
                        Message.objects.filter(
                            Q(sender=OuterRef('id'),reciever=user_id) |
                            Q(reciever=OuterRef('id'),sender=user_id)
                        ).order_by('-id')[:1].values_list('id',flat=True)
                    )
                ).values_list('last_msg', flat=True).order_by("-id")
            )
        ).order_by("-id")
        return messages


class SearchUserAPIView(generics.GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]  

    def get(self, request, username):
        users = self.queryset.filter(Q(username__icontains=username) | Q(email__icontains=username))
        if (users.exists()) is not True:
            return Response({'error': 'Users not found'}, status=status.HTTP_404_NOT_FOUND)
        srz = self.serializer_class(users, many=True)
        return Response(srz.data, status.HTTP_200_OK)