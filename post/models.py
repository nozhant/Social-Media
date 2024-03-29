from django.db import models
from django.utils import timezone

from user.models import UserProfile


def post_file(instance, filename):
    return 'post_{0}/File/{1}'.format(instance.id, filename)


class Post(models.Model):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    caption = models.TextField(
        blank=True,
        null=True
    )

    lat = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    long = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    story = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )

    created_date = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True
    )

    number_of_saved = models.IntegerField(default=0)
    number_of_like_out_followers = models.IntegerField(default=0)
    number_of_comment_out_followers = models.IntegerField(default=0)


class Tag(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    user = models.ManyToManyField(
        UserProfile,
        related_name='user_tags'
    )


class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    user = models.ManyToManyField(
        UserProfile,
        related_name='user_likes'
    )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )

    text = models.TextField(
        blank=True,
        null=True
    )


class PostFile(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to=post_file
    )


class UserFav(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
