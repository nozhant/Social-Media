from django.db import models
from user.models import UserProfile


class Post(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    description = models.TextField()

    # todo: tag people

    lat = models.CharField(max_length=50)

    long = models.CharField(max_length=50)


class PostFile(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    file = models.FileField()
