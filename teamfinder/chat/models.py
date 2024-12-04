from django.db import models
from teamfinder_app.models import User, Team

class ChatGroup(models.Model):
    group_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, related_name='teamchats', null=True, on_delete=models.CASCADE)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True, on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name='chat_groups', blank=True)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.group_id)

    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author.username} : {self.body}'

    class Meta:
        ordering = ['-created']