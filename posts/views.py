from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.contrib.auth import get_user_model
User = get_user_model()

from permissions import IsAuthenticated, IsOwner2
from .models import Post, File, SavePost, Comment, Like
from accounts.models import Follow
from .serializers import (CreatePostSerializer,
                          PostSerializer,
                          SavePostSerializer,
                          ListSavePostsSerializer,
                          CommentSerializer,
                          ReplySerializer,
                          LikeSerializer,
                          UserForLikeSerializer,
                          PostForExploreSerializer)
from paginations import CustomPagination, CustomPagination2


class CreatePostAPIView(GenericAPIView):
    serializer_class = CreatePostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        caption = request.data.get('caption')
        files = request.FILES.getlist('files')
        files_count = len(files)
        if not (1 <= files_count <= 10):
            return Response(f'Number of files should be between 1 and 10. Received {files_count} files.', status=status.HTTP_401_UNAUTHORIZED)
        for file in files:
            if File(file=file).file_type() == 'unacceptable':
                return Response('File extension is not acceptable.', status=400)
        post = Post.objects.create(user=request.user, caption=caption)
        File.objects.bulk_create([File(file=file, post=post) for file in files])
        return Response('Post created.', status=status.HTTP_201_CREATED)


class DeletePostAPIView(GenericAPIView):
    serializer_class = CreatePostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            self.check_object_permissions(request, obj=post)
            post.delete()
            return Response({'message':'You deleted your post'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)


class PostAPIView(GenericAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, post_id):
        try:
            to_user = User.objects.get(pk=user_id)
            follow = Follow.objects.filter(from_user=request.user, to_user=to_user)
            if (follow is not True) and (to_user.private):
                return Response({'error':'This account is privte and you can not see its post'}, status=status.HTTP_400_BAD_REQUEST)
            post = Post.objects.get(pk=post_id)
            if (follow) or ((to_user.private) is not True):
                srz = self.serializer_class(post)
                return Response(srz.data, status=status.HTTP_200_OK)
            return Response({'error':'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        

class UpdatePostAPIView(GenericAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]

    def put(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            self.check_object_permissions(request, obj=post)
            new_caption = request.data.get('caption')
            post.caption = new_caption
            post.save()
            return Response({'message':'You updated the caption'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)


class HomeAPIView(GenericAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        following_ids = user.followings.select_related('to_user').values_list('to_user__id', flat=True)
        posts = Post.objects.filter(user__id__in=following_ids).order_by('-created_at')
        srz = self.serializer_class(posts, many=True)
        return Response(srz.data, status=status.HTTP_200_OK)


class SavePostAPIView(GenericAPIView):
    serializer_class = SavePostSerializer
    queryset = SavePost.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            SavePost.objects.create(user=request.user, post=post)
            return Response({'message':'The post has been saved'}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteSavePostAPIView(GenericAPIView):
    serializer_class = SavePostSerializer
    queryset = SavePost.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            save_post = SavePost.objects.get(user=request.user, post=post)
            self.check_object_permissions(request, obj=save_post)
            save_post.delete()
            return Response({'message':'The post has been deleted'}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except SavePost.DoesNotExist:
            return Response({'error':'Save Post not found'}, status=status.HTTP_400_BAD_REQUEST)


class ListSavePostsAPIView(GenericAPIView):
    serializer_class = ListSavePostsSerializer
    queryset = SavePost.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        save_posts = SavePost.objects.filter(user=request.user)
        if save_posts.exists():
            srz = self.serializer_class(save_posts, many=True)
            return Response(srz.data, status=status.HTTP_200_OK)
        else:
            return Response({'message':'There is no save post'}, status=status.HTTP_204_NO_CONTENT)


class CreateCommentAPIView(GenericAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            body = request.data.get('body')
            post = Post.objects.get(pk=post_id)
            Comment.objects.create(user=request.user, post=post, body=body)
            return Response({'message':'Comment has been created'}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        

class DeleteCommentAPIView(DestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]


class ReplyCommentAPIView(GenericAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def post(self, request, post_id, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
            body = request.data.get('body')
            post = Post.objects.get(pk=post_id)
            Comment.objects.create(user=request.user, post=post, body=body, reply=comment, is_reply=True)
            return Response({'message':'Reply has been created'}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error':'Comment not found'}, status=status.HTTP_400_BAD_REQUEST)
        

class ListCommentsAPIView(GenericAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination  

    def get(self, request, user_id, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            comments = Comment.objects.filter(post=post)
            user = User.objects.get(pk=user_id)
            follow = Follow.objects.filter(from_user=request.user, to_user=user)
            if (follow.exists()) or ((user.private) is not True) or (request.user == user):
                page = self.paginate_queryset(comments)  
                if page is not None:
                    srz = self.serializer_class(page, many=True)
                    return self.get_paginated_response(srz.data)  
                srz = self.serializer_class(comments, many=True)
                return Response(srz.data, status=status.HTTP_200_OK)
            else:
                return Response({'error':'You can not see the comments this post'}, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error':'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Follow.DoesNotExist:
            return Response({'error':'Follow not found'}, status=status.HTTP_400_BAD_REQUEST)


class ListRepliesAPIView(GenericAPIView):
    serializer_class = ReplySerializer
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination 

    def get(self, request, user_id, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
            user = User.objects.get(pk=user_id)
            follow = Follow.objects.filter(from_user=request.user, to_user=user)
            replies = comment.rcomments.all().order_by('created_at')
            if (follow.exists()) or ((user.private) is not True) or (request.user == user):
                page = self.paginate_queryset(replies)  
                if page is not None:
                    srz = self.serializer_class(page, many=True)
                    return self.get_paginated_response(srz.data)  
                srz = self.serializer_class(replies, many=True)
                return Response(srz.data, status=status.HTTP_200_OK)
            else:
                return Response({'error':'You can not see the replies this comment'}, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error':'Comment not found'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error':'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Follow.DoesNotExist:
            return Response({'error':'Follow not found'}, status=status.HTTP_400_BAD_REQUEST)


class CreateLikeAPIView(GenericAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            if Like.objects.filter(user=request.user, post=post).exists():
                return Response({'You already liked this post'})
            Like.objects.create(user=request.user, post=post)
            return Response({'message':'Like has been created'}, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_400_BAD_REQUEST)


class DeleteLikeAPIView(DestroyAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated, IsOwner2]


class ListLikesAPIView(GenericAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, post_id):
        user = User.objects.get(pk=user_id)
        post = Post.objects.get(pk=post_id)
        follow = Follow.objects.filter(from_user=request.user, to_user=user).exists()
        if (follow) or (user == request.user) or ((user.private) is not True):
            likes = post.plikes.all()
            users = [like.user for like in likes]
            page = self.paginate_queryset(users)
            if page is not None:
                srz = UserForLikeSerializer(page, many=True)
                return self.get_paginated_response(srz.data)
            srz = self.serializer_class(users, many=True)
            return Response(srz.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You can not see post likers'}, status=status.HTTP_400_BAD_REQUEST)


class ExploreAPIView(GenericAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination2

    def get(self, request):
        posts = Post.objects.annotate(likes_count=Count('plikes')).filter(user__private=False).order_by('-likes_count')
        page = self.paginate_queryset(posts)
        if page is not None:
            srz = PostForExploreSerializer(page, many=True)
            return self.get_paginated_response(srz.data)
        srz = PostForExploreSerializer(posts, many=True)
        return Response(srz.data, status=status.HTTP_200_OK)
