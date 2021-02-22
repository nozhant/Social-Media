from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from post.serializers import *
from response_management.EMS import *


class UserPost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_posts = Post.objects.filter(user=request.user)

        _list = []
        for p in user_posts:
            tags = Tag.objects.filter(post=p)
            files = PostFile.objects.filter(post=p)
            likes = Like.objects.filter(post=p)
            comments = Comment.objects.filter(post=p)
            ctx = {
                'post': PostSerializer(p).data,
                'files': PostFilesSerializer(files, many=True).data,
                'tags': PostTagSerializer(tags, many=True).data,
                'likes': PostLikeSerializer(likes, many=True).data,
                'comments': PostCommentSerializer(comments, many=True).data,
            }
            _list.append(ctx)

        return successful_response(_list)

    def post(self, request):
        pass
