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


class UserStory(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_obj = UserProfile.objects.filter(id=request.user.id).first()
        if not user_obj:
            return existence_error('user')

        user_serialized = UserProfileGetSerializer(user_obj)

        user_stories = Post.objects.filter(user=user_obj, story=True)

        story_list = []
        for p in user_stories:
            tags = Tag.objects.filter(post=p)
            files = PostFile.objects.filter(post=p)
            ctx = {
                'story': PostSerializer(p).data,
                'files': PostFilesSerializer(files, many=True).data,
                'tags': PostTagSerializer(tags, many=True).data,
            }
            story_list.append(ctx)

        followers = user_serialized.data.get('follower')

        for f in list(followers):
            f = dict(f)
            user_stories = Post.objects.filter(user__id=f.get('id'), story=True)
            for p in user_stories:
                tags = Tag.objects.filter(post=p)
                files = PostFile.objects.filter(post=p)
                ctx = {
                    'story': PostSerializer(p).data,
                    'files': PostFilesSerializer(files, many=True).data,
                    'tags': PostTagSerializer(tags, many=True).data,
                }
                story_list.append(ctx)

        return successful_response(story_list)
