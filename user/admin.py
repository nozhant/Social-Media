from django.contrib import admin

from user.models import UserProfile, Otp, UserFollower, UserFollowing


admin.site.register(UserProfile)
admin.site.register(UserFollower)
admin.site.register(UserFollowing)
admin.site.register(Otp)
