from cache_memoize import cache_memoize
from django.db.models import F
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


@cache_memoize(3600)
def get_posts(user_obj):
    following = UserFollowing.objects.filter(user=user_obj).first()

    following_serialized = UserFollowingShowSerializer(following)

    post_list = []

    for f in following_serialized.data.get('following'):
        f = dict(f)
        user_posts = Post.objects.filter(user__id=f.get('id'), story=False).order_by('-created_date')
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

    return post_list


class UserHome(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user_obj = UserProfile.objects.filter(id=request.user.id).first()

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

        following = UserFollowing.objects.filter(user=user_obj).first()

        following_serialized = UserFollowingShowSerializer(following)

        for f in following_serialized.data.get('following'):
            f = dict(f)
            user_stories = Post.objects.filter(user__id=f.get('id'), story=True).order_by('-created_date')
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

    def post(self, request):
        p = request.data.get('page', 1)

        user_obj = UserProfile.objects.filter(id=request.user.id).first()
        if not user_obj:
            return existence_error('user')

        post_list = get_posts(user_obj)

        return successful_response(post_list[2 * (int(p) - 1): 2 * (int(p))])


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

        post = Post.objects.filter(id=post_id)

        user_post = post.first().user

        follower = UserFollower.objects.filter(user=user_post, follower__id=request.user.id)

        if like.exists():
            like = like.first()
            if set_like == '1':
                like.user.add(request.user.id)

                if not follower.exists():
                    post.update(number_of_like_out_followers=F('number_of_like_out_followers') + 1)
                    UserProfile.objects.filter(id=user_post.id).update(
                        number_of_liked_posts_out_followers=F('number_of_liked_posts_out_followers') + 1
                    )
            else:
                like.user.remove(request.user.id)

                if not follower.exists():
                    post.update(number_of_like_out_followers=F('number_of_like_out_followers') - 1)
                    UserProfile.objects.filter(id=user_post.id).update(
                        number_of_liked_posts_out_followers=F('number_of_liked_posts_out_followers') - 1
                    )
        else:
            like = Like.objects.create(post_id=post_id)
            like.user.add(request.user.id)

            if not follower.exists():
                post.update(number_of_like_out_followers=F('number_of_like_out_followers') + 1)
                UserProfile.objects.filter(id=user_post.id).update(
                    number_of_liked_posts_out_followers=F('number_of_liked_posts_out_followers') + 1
                )

        return successful_response({})

    def post(self, request):

        post_id = request.data.get('post_id')
        post = Post.objects.filter(id=post_id)
        user_post = post.first().user
        follower = UserFollower.objects.filter(user=user_post, follower__id=request.user.id)

        if not follower.exists():
            post.update(number_of_comment_out_followers=F('number_of_comment_out_followers') + 1)
            UserProfile.objects.filter(id=user_post.id).update(
                number_of_comment_posts_out_followers=F('number_of_comment_posts_out_followers') + 1
            )

        comment = Comment.objects.create(post_id=post_id, user=request.user, text=request.data.get('text'))

        return successful_response(PostCommentSerializer(comment).data)


class UserFavPost(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        post_id = request.data.get('post_id')

        ctx = {'user_id': request.user.id}
        ctx.update({'post_id': post_id})

        fav = request.data.get('fav')

        if fav == 1:
            Post.objects.filter(id=post_id).update(number_of_saved=F('number_of_saved') + 1)
            UserProfile.objects.filter(id=post_id.first().user.id).update(
                number_of_saved_posts=F('number_of_saved_posts') + 1
            )
            UserFav.objects.create(**ctx)
        else:
            Post.objects.filter(id=post_id).update(number_of_saved=F('number_of_saved') - 1)
            UserProfile.objects.filter(id=post_id.first().user.id).update(
                number_of_saved_posts=F('number_of_saved_posts') - 1
            )
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
