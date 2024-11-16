import teamfinder_app.tuapi as tu
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import django.contrib.auth.models as authmodel
from django.contrib.auth import authenticate, login, logout, get_user
from teamfinder_app.models import User, Post, RecruitPost, ResultPost, Feedback, TeamMember, Team, Requirement, Faculty, Major
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
                    faculty=data["faculty"],
                    year=year
                )
                user_profile.save()

                faculty = Faculty.objects.get_or_create(
                    name=data["faculty"], slug=data["faculty"], faculty=data["faculty"]
                )

                major = Major.objects.get_or_create(
                    name=data["department"], slug=data["department"], major=data["department"]
                )

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
    current_joinedteams = TeamMember.objects.filter(member=user)
    current_leadteams = Team.objects.filter(team_leader=user)
    resultpost = ResultPost.objects.filter(post__user=user)
    feedback = Feedback.objects.filter(receiver=user)
    context = {
        "user_id": user.user_id,
        "userdata": user,
        "created_post": created_post,
        "current_joinedteams": current_joinedteams,
        "current_leadteams" : current_leadteams,
        "resultpost": resultpost,
        "feedback": feedback,
    }

    return render(request, 'myaccount.html', context)


#Logout
def web_logout(request):
    logout(request)
    return redirect('/login')


#Recruitment Post
def recruitment(request):
    recruit_posts = RecruitPost.objects.filter(status=True)

    posts = []
    for post in recruit_posts:
        posts.append(post.post)

    context = {
        "posts": posts,
    }

    return render(request, 'recruitment.html', context)


#Result Post
def result(request):
    result_posts = ResultPost.objects.all()

    posts = []
    for post in result_posts:
        posts.append(post.post)

    context = {
        "post": post
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
        heading = request.POST.get('heading')
        content = request.POST.get('content')
        amount = request.POST.get('amount')
        tags = [tag.strip() for tag in request.POST.get('tag').split(',')]

        if len(tags) > 3:
            context = {
                "heading": heading,
                "content": content,
                "amount": amount,
                "tags": tags
            }

            return render(request, 'create.html', context)

        request.session['heading'] = heading
        request.session['content'] = content
        request.session['amount'] = amount
        request.session['tags'] = tags

        return redirect('/create/requirement')

    return render(request, 'create.html')


#Requirement
def web_requirement(request):
    user = User.objects.get(user_id=get_user(request))
    heading = request.session.get('heading')
    content = request.session.get('content')
    amount = request.session.get('amount')
    tags = request.session.get('tags')

    if request.method == 'POST':
        req_faculty = [faculty.strip() for faculty in request.POST.get('req_faculty').split(',')]
        req_major = [major.strip() for major in request.POST.get('req_major').split(',')]
        year = request.POST.get('year')
        description = request.POST.get('description')

        post = Post.objects.create(
            user=user,
            heading=heading,
            content=content,
            amount=amount
        )
        post.save()

        recruit = RecruitPost.objects.create(
            post=post,
            status=True
        )
        recruit.tag.set(tags)
        recruit.save()

        requirement = Requirement.objects.create(
            post=recruit,
            year=year,
            description=description
        )
        requirement.req_faculty.set(req_faculty)
        requirement.req_major.set(req_major)
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


