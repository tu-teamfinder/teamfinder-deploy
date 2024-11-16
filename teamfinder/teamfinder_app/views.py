import teamfinder_app.tuapi as tu
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import django.contrib.auth.models as authmodel
from django.contrib.auth import authenticate, login, logout, get_user
from teamfinder_app.models import User, Post, RecruitPost, ResultPost, Requirement, FeedbackMessage, Registration
from django.core.exceptions import ObjectDoesNotExist
from taggit.models import Tag

# Create your views here.

#Homepage
def homepage(request):
    return render(request, 'homepage.html')


#About
def about(request):
    return render(request, 'about.html')


#Login
def web_login(request):
    if request.user.is_authenticated:
        return redirect('/myaccount')

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
                    faculty=data["fuculty"],
                    year=year
                )
                user_profile.save()

                Tag.objects.get_or_create(name=data["department"])
                Tag.objects.get_or_create(name=data["faculty"])

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
    user = User.objects.get(user_id=get_user(request))
    created_post = RecruitPost.objects.filter(post__user=user)
    current_teams = Registration.objects.filter(user=user)
    outcome = ResultPost.objects.filter(post__user=user)
    feedback = FeedbackMessage.objects.filter(receiver=user)
    # ต้องเอา created_post ใส่ด้วย ^

    context = {
        "user_id": user.user_id,
        "userdata": user,
        "created_post": created_post,
        "current_teams": current_teams,
        "outcome": outcome,
        "feedback": feedback,
    }

    return render(request, 'myaccount.html', context)


#Logout
def web_logout(request):
    logout(request)
    return redirect('/login')


#Recruitment Post
def recruitment(request):
    user = User.objects.get(user_id=get_user(request))
    user_tag = [user.major, user.year, 'all']
    recruit_posts = [
        RecruitPost.objects.filter(tag__in=user_tag)
    ]

    posts = []
    status = []
    for post in recruit_posts:
        posts.append(post.post)
        status.append(post.status)

    context = {
        "posts": posts,
        "status": status
    }

    return render(request, 'recruitment.html', context)


#Result Post
def result(request):
    user = User.objects.get(user_id=get_user(request))
    result_posts = ResultPost.objects.all()

    context = {
        "result_posts": result_posts
    }

    return render(request, 'result.html', context)


#Post
def web_post(request, post_id):
    post = Post.objects.filter(post_id=post_id).first()

    if post is None:
        return render(request, 'pagenotfound.html')

    is_result = (ResultPost.objects.filter(post=post).first() is not None)

    context = {
        "user": post.user,
        "heading": post.heading,
        "content": post.content,
        "timestamp": post.timestamp,
        "is_result": is_result
    }

    return render(request, 'post.html', context)


#Create Post
def create_post(request):
    if request.method == 'POST':
        user = User.objects.get(user_id=get_user(request))
        heading = request.POST.get('heading')
        content = request.POST.get('content')
        amount = request.POST.get('amounnt')

        
        post = Post.objects.create(
            user=user,
            heading=heading,
            content=content
        )
        post.save()

        return web_requirement(request, post)

    return render(request, 'create.html')


#Requirement
def web_requirement(request, post):
    if request.method == 'POST':
        tag = None
        req_faculty = None
        req_major = None
        year = None
        description = None

        recruit = RecruitPost.objects.create(
            post=post,
            tag=tag,
            status=True
        )
        recruit.save()

        requirement = Requirement.objects.create(
            post=recruit,
            req_faculty=req_faculty,
            req_major = req_major,
            year = year,
            description = description
        )
        requirement.save()

        return redirect('/recruitment')

    return render(request, 'requirement.html')


#Team
def team(request):
    user = User.objects.get(user_id=get_user(request))
    active = None
    finished = None

    context = {
            "active": active,
            "finished": finished
    }

    return render(request, 'team.html', context)


#Finish
def finish(request, post):

    return post_result(request, post)


#Post result
def post_result(request, post):
    if request.method == 'POST':
        user = User.objects.get(user_id=get_user(request))
        heading = request.POST.get('heading')
        content = request.POST.get('content')
        tag = None

        recruit = RecruitPost.objects.get(post=post)
        recruit.delete()

        res = ResultPost.objects.create(
            post=post,
            tag=tag
        )

        return redirect('/result')

    context = {
        "heading": post.heading,
        "content": post.content
    }

    return render(request, 'post_result.html', context)


#Search
def search(request, search_context):
    return render()


#Message
def message_history(request, receiver):
    return render()


#Help
def help(request):
    return render(request, 'help.html')


