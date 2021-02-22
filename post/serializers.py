from post.models import *
from user.serializers import *
from rest_framework import serializers


class PostSerializer(ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


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
    user = UserProfileForPostSerializer(many=True)

    class Meta:
        model = Comment
        exclude = (
            'post',
        )
