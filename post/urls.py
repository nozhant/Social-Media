from django.urls import path

from post.views import *

urlpatterns = [
    path('user-post/', UserPost.as_view()),
    path('user-home/', UserHome.as_view()),
    path('like/', PostView.as_view()),
    path('comment/', PostView.as_view()),
    path('fav/', UserFavPost.as_view()),
]
