from django.urls import path

from post.views import *

urlpatterns = [
    path('user-post/', UserPost.as_view()),
]
