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


class PostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        post_id = request.GET.get('id')
        like = Like.objects.filter(post_id=post_id)
        tags = Tag.objects.filter(post_id=post_id)
        comments = Comment.objects.filter(post_id=post_id)

        ctx = {
            'likes': PostLikeSerializer(like, many=True).data,
            'tags': PostTagSerializer(tags, many=True).data,
            'comments': PostCommentSerializer(comments, many=True).data,
        }

        return successful_response(ctx)

    def put(self, request):
        post_id = request.GET.get('id')
        set_like = request.GET.get('like')

        like = Like.objects.filter(post_id=post_id)
        if like.exists():
            like = like.first()
            if set_like == '1':
                like.user.add(request.user.id)
            else:
                like.user.remove(request.user.id)
        else:
            like = Like.objects.create(post_id=post_id)
            like.user.add(request.user.id)

        return successful_response({})

    def post(self, request):

        comment = Comment.objects.create(**request.data)

        return successful_response(PostCommentSerializer(comment).data)


class UserFavPost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ctx = {'user_id': request.user.id}
        ctx.update({'post_id': request.data.get('post_id')})

        fav = request.data.get('fav')

        if fav == 1:
            UserFav.objects.create(**ctx)
        else:
            UserFav.objects.filter(**ctx).delete()

        return successful_response({})

    def get(self, request):

        favs = UserFav.objects.filter(user_id=request.user.id)

        fav_list = UserFavPostSerializer(favs, many=True).data

        index = 0
        for f in favs:
            ctx = fav_list[index]
            post_id = f.post.id

            files = PostFile.objects.filter(post_id=post_id)

            ctx.update({'files': PostFilesSerializer(files, many=True).data})

            index += 1

        return successful_response(fav_list)


class Search(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()

        max = 0
        for p in posts:
            c = Like.objects.filter(post=p)
            if c.exists():
                c = c.first().user.count()
                if c > max:
                    max = c

        max /= 2
        max = int(max)

        if request.GET.get('query') is not None:
            posts = Post.objects.filter(caption__contains=request.GET.get('query'))
        post_list = []

        for p in posts:
            c = Like.objects.filter(post=p)
            if c.exists():
                c = c.first().user.count()

                if c > max:
                    files = PostFile.objects.filter(post=p)

                    ctx = {
                        'post': PostSerializer(p).data,
                        'files': PostFilesSerializer(files, many=True).data
                    }
                    post_list.append(ctx)

        return successful_response(post_list)
