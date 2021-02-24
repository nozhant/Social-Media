from post.models import *
from user.serializers import *
from rest_framework import serializers


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class StorySerializer(ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_user(self, obj):
        u = obj.user
        return UserProfileForPostSerializer(u).data


class PostFilesSerializer(ModelSerializer):
    class Meta:
        model = PostFile
        exclude = (
            'post',
        )


class PostTagSerializer(ModelSerializer):
    user = UserProfileForPostSerializer(many=True)

    class Meta:
        model = Tag
        exclude = (
            'post',
        )


class PostLikeSerializer(ModelSerializer):
    user = UserProfileForPostSerializer(many=True)

    class Meta:
        model = Like
        exclude = (
            'post',
        )


class PostCommentSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        exclude = (
            'post',
        )

    def get_user(self, obj):
        u = obj.user
        return UserProfileForPostSerializer(u).data


class UserFavPostSerializer(ModelSerializer):
    user = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user']

    def get_user(self, obj):
        u = obj.user
        return UserProfileForPostSerializer(u).data

    def get_post(self, obj):
        p = obj.post
        return PostSerializer(p).data
