from django.urls import path

from post.views import *

urlpatterns = [
    path('create/', CreatePost.as_view()),
]
