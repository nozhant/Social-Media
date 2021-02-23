from django.db import models
from datetime import datetime
from django.utils import timezone

from user.models import UserProfile


class Conversation(models.Model):

    users = models.ManyToManyField(
        UserProfile,
        related_name='users'
    )

    creator = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='conversation_creator'
    )

    time = models.FloatField(
        default=datetime.timestamp(timezone.now()),
        blank=True,
        null=True
    )  # timestamp

    date = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True
    )


class Message(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='conversation'
    )

    message_creator = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='message_creator'
    )

    body = models.TextField(
        blank=True,
        null=True
    )

    time = models.FloatField(
        default=datetime.timestamp(timezone.now()),
        blank=True,
        null=True
    )  # timestamp

    date = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True
    )

    users_seen = models.ManyToManyField(
        UserProfile,
        blank=True,
        related_name='users_seen'
    )

