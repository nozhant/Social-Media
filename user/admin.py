from django.contrib import admin

from user.models import UserProfile, Otp


admin.site.register(UserProfile)
admin.site.register(Otp)