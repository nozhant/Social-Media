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

        temp = {'user': request.user.id}
        temp.update(request.data)

        post_serial = PostSerializer(data=temp)

        if not post_serial.is_valid():
            return validate_error(post_serial)

        if request.data.get('story'):
            story = Post.objects.filter(user=request.user, story=True)
            if story.exists():
                return unsuccessful_response(message='you have a story, remove it first', status=200)

        post_serial.save()

        tag = Tag.objects.create(post_id=post_serial.data.get('id'))
        tag.user.add(*request.data.get('tag_peoples'))

        return successful_response(post_serial.data)

    def put(self, request):
        num_of_file = len(request.FILES)

        files = []
        for i in range(0, num_of_file):
            files.append(
                PostFile.objects.create(
                    post_id=request.data.get('id'),
                    file=request.FILES.get('file{}'.format(str(i))),
                ),
            )

        return successful_response(PostFilesSerializer(files, many=True).data)

    def delete(self, request):
        Post.objects.filter(id=request.GET.get('id')).delete()
        return successful_response({})


class UserHome(APIView):
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

        post_list = []

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

            user_posts = Post.objects.filter(user__id=f.get('id'), story=False)
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
                post_list.append(ctx)

        ctx = {
            'stories': story_list,
            'posts': post_list,
        }

        return successful_response(ctx)
