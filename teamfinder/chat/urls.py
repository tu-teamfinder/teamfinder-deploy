from django.urls import path
from chat import views

urlpatterns = [
    path('chat/<group_id>', views.chat_view, name="team-chat"),
]