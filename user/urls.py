from django.urls import path

from user.views import (
    Register,
    Login,
    Profile,
    ChangePassword,
    FollowOrUnfollow,
    ForgetPassword,
    ResetPassword,
    Logout,
    TwoStepVerificationLogin
)

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('two-step', TwoStepVerificationLogin.as_view()),
    path('logout', Logout.as_view()),
    path('profile', Profile.as_view()),
    path('change-password', ChangePassword.as_view()),
    path('follow-unfollow', FollowOrUnfollow.as_view()),
    path('forget-password', ForgetPassword.as_view()),
    path('reset-password', ResetPassword.as_view())
]
