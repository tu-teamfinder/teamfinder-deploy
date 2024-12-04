from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, HttpResponse
from chat.models import *
from chat.forms import *
from teamfinder_app.models import Team, TeamMember

@login_required
def chat_view(request, group_id):
    user = request.user
    chat_list = ChatGroup.objects.filter(members=user)

    if not chat_list:
        return render(request, 'no_chat.html')

    if group_id == 'default':
        chat_group = ChatGroup.objects.filter(members=user).first()
        return redirect(f'/chat/{chat_group.group_id}')

    chat_group = get_object_or_404(ChatGroup, group_id=group_id)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = ChatmessageCreateForm()
    
    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid:
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {
                'message' : message,
                'user' : request.user
            }
            return render(request, 'chat_message_p.html', context)

    context = {
        'chat_messages' : chat_messages, 
        'form' : form,
        'group_id' : group_id,
        'chat_group' : chat_group,
        'chat_list': chat_list 
    }
    
    return render(request, 'chat.html', context)