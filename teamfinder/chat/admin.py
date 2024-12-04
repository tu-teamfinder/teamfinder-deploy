from django.contrib import admin
from chat.models import *

admin.site.register(ChatGroup)
admin.site.register(GroupMessage)