from django.urls import path
from chat.consumers import *

websocket_urlpatterns = [
    path("ws/chatroom/<group_id>", ChatroomConsumer.as_asgi()),
]