from django.contrib import admin
from post.models import *

admin.site.register(Post)
admin.site.register(PostFile)
admin.site.register(Tag)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(UserFav)

