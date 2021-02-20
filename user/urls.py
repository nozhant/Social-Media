from django.urls import path

from user.views import (
    Register,
    Login

)

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
]
