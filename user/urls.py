from django.urls import path

from user.views import (
    Register,
    Login,
    Profile,
    ChangePassword,
    FollowOrUnfollow

)

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('profile', Profile.as_view()),
    path('change-password', ChangePassword.as_view()),
    path('follow-unfollow', FollowOrUnfollow.as_view())
]
