from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json
from chat.models import *

class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.chatroom = get_object_or_404(ChatGroup, group_id=self.group_id)
        
        async_to_sync(self.channel_layer.group_add)(
            self.group_id, self.channel_name
        )   
        
        self.accept()
        
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_id, self.channel_name
        )
        
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']
        
        message = GroupMessage.objects.create(
            body = body,
            author = self.user, 
            group = self.chatroom 
        )
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.group_id, event
        )
        
    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        html = render_to_string("chat_message_p.html", context=context)
        self.send(text_data=html)