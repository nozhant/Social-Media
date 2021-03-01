from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone


def profile_image_directory(instance, filename):
    return 'user_{0}/ProfilePhoto/{1}'.format(instance.id, filename)


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

    profile_photo = models.FileField(
        upload_to=profile_image_directory,
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    website = models.URLField(
        blank=True,
        null=True
    )

    two_step = models.BooleanField(
        default=False,
        blank=True,
        null=True
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

    business = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    country = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    city = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    objects = UserProfileManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []


class UserFollowing(models.Model):

    user_id = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    following_user_id = models.ManyToManyField(
        UserProfile,
        related_name="followings",
    )


class UserFollower(models.Model):

    user_id = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    follower_user_id = models.ManyToManyField(
        UserProfile,
        related_name="followers",
    )


class Otp(models.Model):

    email_phone = models.CharField(
        max_length=128,
        blank=True,
        null=True
    )

    code = models.CharField(
        max_length=5,
        blank=True,
        null=True
    )








