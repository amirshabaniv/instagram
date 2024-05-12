from .utils import send_generated_otp_to_email
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .serializers import (LoginSerializer,
                          LogoutUserSerializer,
                          UserRegisterSerializer,
                          PasswordResetRequestSerializer,
                          SetNewPasswordSerializer,
                          PasswordResetTokenGenerator,
                          UserRegisterSerializer,
                          VerifySerializer,
                          UserSerializer,
                          ForPrivateUserSerializer,
                          FollowSerializer,
                          FollowRequestSerializer,
                          FollowerSerializer,
                          FollowingSerializer,
                          StorySerializer,
                          StoryViewSerializer)
from .models import OneTimePassword, Follow, FollowRequest, Story, StoryView
from permissions import IsOwner, IsAuthenticated, IsOwner2
from paginations import CustomPagination

from django.contrib.auth import get_user_model
User = get_user_model()


class RegisterView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user = request.data
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(GenericAPIView):
    serializer_class = VerifySerializer

    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequestView(GenericAPIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
    

class PasswordResetConfirm(GenericAPIView):

    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)


class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'You logged out'}, status=status.HTTP_204_NO_CONTENT)
 

class UserAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get(self, request, username):
        user = User.objects.get(username=username)
        follow = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        if (user.private and follow) or ((user.private) is not True) or (user == request.user):
            srz = self.serializer_class(user)
            return Response(srz.data, status=status.HTTP_200_OK)
        
        elif (user.private) and (follow is not True):
            srz = ForPrivateUserSerializer(user)
            return Response(srz.data, status=status.HTTP_200_OK)
    
    def put(self, request, username):
        user = User.objects.get(username=username)
        self.check_object_permissions(request, obj=user)
        srz = UserSerializer(instance=user, data=request.data, partial=True)
        srz.is_valid(raise_exception=True)
        srz.save()
        return Response(srz.data, status=status.HTTP_200_OK)


class FollowAPIView(GenericAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        from_user = request.user
        to_user = User.objects.get(pk=user_id)
        if from_user == to_user:
            return Response({'message':'You can not follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            follow_request = FollowRequest.objects.filter(from_user=request.user, to_user=to_user).exists()
            follow = Follow.objects.filter(from_user=request.user, to_user=to_user).exists()
            if follow or follow_request:
                return Response({'message':'You already sent follow request or followed this account'}, status=status.HTTP_400_BAD_REQUEST)
            if to_user.private:
                follow_request = FollowRequest.objects.create(from_user=from_user, to_user=to_user)
                follow_request.follow_request()
                return Response({'message': 'Follow request sent. Wait for approval.'}, status=status.HTTP_200_OK)
            else:
                Follow.objects.create(from_user=request.user, to_user=to_user)
                return Response({'message': 'Follow created.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message':'User not found'}, status=status.HTTP_404_NOT_FOUND)


class FollowRequestResponseAPIView(GenericAPIView):
    queryset = FollowRequest.objects.all()
    serializer_class = FollowRequestSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        follow_requests = FollowRequest.objects.filter(to_user=request.user)
        srz = self.serializer_class(follow_requests, many=True)
        return Response(srz.data, status=status.HTTP_200_OK)
    
    def post(self, request, follow_request_id):
        response = request.data.get('response')
        try:
            follow_request = FollowRequest.objects.get(pk=follow_request_id)
            follow_request.response_to_follow_request(response)
            if response == 'Accept':
                Follow.objects.create(from_user=follow_request.from_user, to_user=request.user)
                return Response({'message':f'You {response.lower()}ed the follow request.'}, status=status.HTTP_200_OK)
            elif response == 'Reject':
                return Response({'message':f'You {response.lower()}ed the follow request.'})
            return Response({'message':'Invalid response provided'})
        except FollowRequest.DoesNotExist:
            return Response({'message':'Follow request not found'}, status=status.HTTP_404_NOT_FOUND)
        

class UnfollowAPIView(GenericAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        from_user = request.user
        to_user = User.objects.get(pk=user_id)
        if from_user == to_user:
            return Response({'message':'You can not unfollow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            follow = Follow.objects.filter(from_user=from_user, to_user=to_user).exists()
            if follow is not True:
                return Response({'message':'You did not follow this account'}, status=status.HTTP_400_BAD_REQUEST)
            if follow:
                follow.delete()
            follow_request = FollowRequest.objects.filter(from_user=from_user, to_user=to_user).exists()
            if follow_request:
                follow_request.delete()
        except Follow.DoesNotExist:
            return Response({'message':'Follow or follow request not found'}, status=status.HTTP_404_NOT_FOUND)


class FollowersAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = FollowerSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = User.objects.get(username=username)
        follow = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        if (follow) or (user == request.user) or ((user.private) is not True):
            followers = user.followers.all().order_by('id')
            page = self.paginate_queryset(followers)
            if page is not None:
                srz = self.serializer_class(page, many=True)
                return self.get_paginated_response(srz.data)
            srz = self.serializer_class(followers, many=True)
            return Response(srz.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You cannot see this user followers'}, status=status.HTTP_400_BAD_REQUEST)


class FollowingsAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = FollowingSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        user = User.objects.get(username=username)
        follow = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        if (follow) or (user == request.user) or ((user.private) is not True):
            followings = user.followings.all().order_by('id')
            page = self.paginate_queryset(followings)
            if page is not None:
                srz = self.serializer_class(page, many=True)
                return self.get_paginated_response(srz.data)
            srz = self.serializer_class(followings, many=True)
            return Response(srz.data, status=status.HTTP_200_OK)
        else:
            return Response({'message':'You can not see this user followings'}, status=status.HTTP_400_BAD_REQUEST)


class RemoveFollowerAPIView(GenericAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            follow = Follow.objects.filter(from_user=user, to_user=request.user).exists()
            if follow is not True:
                return Response({'message':'this user is not your follower'}, status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response({'message':'The user deleted from your followers'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message':'User not found'}, status=status.HTTP_404_NOT_FOUND)


class CreateStoryAPIView(GenericAPIView):
    serializer_class = StorySerializer
    queryset = Story.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if file:
            story = Story(file=file, user=request.user)
            if story.file_type() == 'unacceptable':
                return Response({'message':'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
            story.save()
            return Response({'message':'Created'}, status=status.HTTP_201_CREATED)
        return Response({'message':'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class StoryAPIView(GenericAPIView):
    serializer_class = StorySerializer
    queryset = Story.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, story_id):
        try:
            viewed_user = User.objects.get(pk=user_id)
            story = Story.objects.get(pk=story_id, user=viewed_user)
            StoryView.objects.get_or_create(viewer=request.user, story=story)
            serializer = StorySerializer(story)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Story.DoesNotExist:
            return Response({'error': 'Story does not exist for the given user.'}, status=status.HTTP_404_NOT_FOUND)


class StoryViewersAPIView(GenericAPIView):
    serializer_class = StoryViewSerializer
    queryset = StoryView.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, story_id):
        story = Story.objects.get(pk=story_id)
        if (story.user == request.user) is not True:   
            return Response({'error':'it is not your story'}, status=status.HTTP_400_BAD_REQUEST)
        viewers = story.views.all()
        srz = self.serializer_class(viewers, many=True)
        viewers_count = story.views.all().count()
        return Response({
            'viewers_count':viewers_count,
            'viewers':srz.data
        }, status=status.HTTP_200_OK)


class RemoveStoryAPIView(GenericAPIView):
    serializer_class = StorySerializer
    queryset = Story.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]

    def delete(self, request, story_id):
        try:
            story = Story.objects.get(pk=story_id)
            self.check_object_permissions(request, obj=story)
            story.delete()
            return Response({'message':'You deleted your story'}, status=status.HTTP_200_OK)
        except Story.DoesNotExist:
            return Response({'error':'Story not found'}, status=status.HTTP_400_BAD_REQUEST)
        
