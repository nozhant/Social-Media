from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone


def profile_image_directory(instance, filename):
    return 'user_{0}/ProfileImage/{1}'.format(instance.id, filename)


class UserProfileManager(BaseUserManager):
    """Manager for user profiles"""

    def create_user(self, username, password=None):
        """create a new user profile"""

        if not username:
            raise ValueError('User Must Provide username')

        user = self.model(username=username)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password):
        """create and save a new superuser with given details"""
        user = self.create_user(username=username, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """Database Model for users"""

    username = models.CharField(
        unique=True,
        max_length=30
    )

    name = models.CharField(
        max_length=128,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=128,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=12,
        blank=True,
        null=True
    )

    profile_photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=profile_image_directory
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    followers = models.IntegerField(
        default=0
    )

    following = models.IntegerField(
        default=0
    )

    number_of_posts = models.IntegerField(
        default=0
    )

    join_date = models.DateTimeField(
        default=timezone.now,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    objects = UserProfileManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []



