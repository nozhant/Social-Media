from django.urls import path

from message.views import *

urlpatterns = [
    path('create', ConversationCreate.as_view()),
    path('list', ConversationList.as_view()),
    path('edit', ConversationEdit.as_view()),
    path('send-message', SendMessage.as_view()),
    path('get-message', GetMessage.as_view()),
    path('conversation-messages', ConversationMessages.as_view()),
    path('message-seen', MessageSeen.as_view()),
]
