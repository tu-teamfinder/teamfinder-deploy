import teamfinder_app.tuapi as tu
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import django.contrib.auth.models as authmodel
from django.contrib.auth import authenticate, login, logout, get_user
import django.contrib.auth as auth
from teamfinder_app.models import User
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

#Homepage
def homepage(request):
    return redirect('/about')


#About
def about(request):
    return render(request, 'about.html')


#Login
def web_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        year = 67 - int(username[0:2]) + 1

        try: 
            user_profile = User.objects.get(user_id=username)
            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect('/myaccount')

        except User.DoesNotExist:
            tu_response = tu.auth(
                user=username,
                password=password
            )
            
            status = tu_response["status"]
            data = tu_response["data"]

            if status == 200:
                user_profile = User.objects.create(
                    user_id=username,
                    password=password,
                    email_address=data["email"],
                    name=data["displayname_en"],
                    major=data["department"],
                    year=year
                )
                user_profile.save()

                create_user = authmodel.User.objects.create_user(
                    username = username,
                    password = password
                )
                create_user.save()

                user = authenticate(
                    request,
                    username=username,
                    password=password
                )

                login(request, user)
                return redirect('/myaccount')
        
        messages.error(request, 'Invalid login')

    return render(request, 'login.html')


#My-account
@login_required(login_url="/login")
def myaccount(request):
    user = str(get_user(request))
    context = {
        "username": user
    }
    return render(request, 'myaccount.html', context)


#Logout
def web_logout(request):
    logout(request)
    return redirect('/login')