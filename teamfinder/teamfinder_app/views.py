import teamfinder_app.tuapi as tu
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, get_user
from teamfinder_app.models import Post, RecruitPost, ResultPost, Feedback, TeamMember, Team
from teamfinder_app.models import UserProfile, Requirement, Faculty, Major, Request, PostComment
from chat.models import ChatGroup
from teamfinder_app.forms import RequestMessageForm, ProfileImageUploadForm, FeedbackForm
from django.core.exceptions import ObjectDoesNotExist
from taggit.models import Tag
from django.db.models import Q, Avg
import json


User = get_user_model()
# Create your views here.

def is_requestable(user, post_id):
    recruit = RecruitPost.objects.filter(post_id=post_id).first()
    if not recruit or not recruit.status:
        return False
    
    requirement = Requirement.objects.get(post=recruit)
    faculty_list = [faculty.name for faculty in requirement.req_faculty.all()]
    major_list = [major.name for major in requirement.req_major.all()]
    faculty_check = user.faculty in faculty_list or "Any" in faculty_list
    major_check = user.major in major_list or "Any" in major_list
    year_check = user.year in list(range(requirement.year_min, requirement.year_max+1))
    requestable = faculty_check | major_check & year_check

    return requestable

#Homepage
def homepage(request):
    current_user = User.objects.count()
    return render(request, 'homepage.html', {"current_user": current_user})

#About
def about(request):
    return render(request, 'about.html')

def web_login(request):
    if request.user.is_authenticated:
        return redirect('/myaccount')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username.isdigit() and len(username) == 10:
            # Extract year logic
            year = 67 - int(username[0:2]) + 1

            # First, try to authenticate with Django's User model
            user = authenticate(
                request, 
                username=username, 
                password=password
            )

            # If user is authenticated
            if user is not None:
                login(request, user)
                return redirect('/myaccount')

            # If User does not exist
            if User.objects.filter(username=username).first() == None:
                # Try authenticating using the external API
                try:
                    tu_response = tu.auth(user=username, password=password)
                    status = tu_response.get("status")
                    data = tu_response.get("data")

                    if status == 200:
                        # User doesn't exist, create them in Django
                        user = User.objects.create_user(
                            username=username,  # Use 'username' as the unique identifier
                            password=password,
                            email_address=data.get("email"),
                            name=data.get("displayname_en"),
                            major=data.get("department"),
                            faculty=data.get("faculty"),
                            year=year,
                        )

                        user.save()

                        # Create user profile
                        UserProfile.objects.create(user=user)

                        # Handle faculty and major
                        faculty = Faculty.objects.get_or_create(
                            name=data["faculty"], slug=data["faculty"], faculty=data["faculty"]
                        )

                        major = Major.objects.get_or_create(
                            name=data["department"], slug=data["department"], major=data["department"]
                        )

                        # Log the user in
                        user = authenticate(request, username=username, password=password)
                        login(request, user)

                        return redirect('/myaccount')
            
                except Exception as e:
                    messages.error(request, 'Error connecting to TU API')
                    print(f"Error during TU API authentication: {e}")
   
            messages.error(request, 'Authentication failed. Invalid credentials.')
        
        else:
            messages.error(request, 'Invalid username format.')

    return render(request, 'login.html')

#My-account
@login_required(login_url="/login")
def myaccount(request):
    user = request.user
    created_post = RecruitPost.objects.filter(post__user=user)
    current_joinedteams = TeamMember.objects.filter(member=user)
    current_leadteams = Team.objects.filter(team_leader=user)
    resultpost = ResultPost.objects.filter(post__user=user)
    feedback = Feedback.objects.filter(receiver=user)

    if request.method == 'POST':
        form = ProfileImageUploadForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()  # Save the updated UserProfile with the new image
            return redirect('/myaccount')  
    else:
        form = ProfileImageUploadForm(instance=request.user.profile)
    
    context = {
        "username": user.username,
        "userdata": user,
        "created_post": created_post,
        "current_joinedteams": current_joinedteams,
        "current_leadteams" : current_leadteams,
        "resultpost": resultpost,
        "feedback": feedback,
        "form": form,
    }
    return render(request, 'myaccount.html', context)

#upload profile
@login_required(login_url="/login")
def upload_profile_image(request):
    if request.method == 'POST':
        form = ProfileImageUploadForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()  # Save the updated UserProfile with the new image
            return redirect('/myaccount')  
    else:
        form = ProfileImageUploadForm(instance=request.user.profile)

    return render(request, 'myaccount.html', {'form': form})

#Logout
def web_logout(request):
    logout(request)
    return redirect('/login')

@login_required(login_url="/login")
def my_stats(request):
    user = request.user
    feedback_set = Feedback.objects.filter(receiver=user)
    labels = ['communication', 'collaboration', 'reliability', 'technical', 'empathy']
    if Feedback.objects.count() != 0:
        average_communication = Feedback.objects.filter(receiver=user).aggregate(Avg('communication_pt'))
        average_collaboration = Feedback.objects.filter(receiver=user).aggregate(Avg('collaboration_pt'))
        average_reliability = Feedback.objects.filter(receiver=user).aggregate(Avg('reliability_pt'))
        average_technical = Feedback.objects.filter(receiver=user).aggregate(Avg('technical_pt'))
        average_empathy = Feedback.objects.filter(receiver=user).aggregate(Avg('empathy_pt'))
        dataset1 = [average_communication['communication_pt__avg'], average_collaboration['collaboration_pt__avg'], 
                    average_reliability['reliability_pt__avg'], average_technical['technical_pt__avg'], average_empathy['empathy_pt__avg']]
    else:
        dataset1 = None
    context = {
        "feedback": feedback_set,
        'labels': json.dumps(labels),
        'dataset1': json.dumps(dataset1),
    }
    return render(request, 'mystats.html', context)


#Recruitment Post
@login_required(login_url="/login")
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
@login_required(login_url="/login")
def result(request):
    result_posts = ResultPost.objects.all()

    posts = []
    for post in result_posts:
        posts.append(post.post)

    context = {
        "posts": posts
    }

    return render(request, 'result.html', context)


#Post
@login_required(login_url="/login")
def web_post(request, post_id):
    user = request.user
    post = Post.objects.filter(post_id=post_id).first()

    if post is None:
        return render(request, 'pagenotfound.html', status=404)

    is_owner = post.user == user
    is_recruit = (RecruitPost.objects.filter(post=post).first() is not None)
    is_requested = Request.objects.filter(user=user, post=post).first()
    status = False
    requestable = False
    
    if is_recruit:
        recruit = RecruitPost.objects.get(post=post)
        status = recruit.status
        
        if status and not is_owner and not is_requested:
            requestable = is_requestable(user, post_id)

    comments = PostComment.objects.filter(post=post).order_by('timestamp')

    context = {
        "post_id": post_id,
        "user": post.user,
        "heading": post.heading,
        "content": post.content,
        "timestamp": post.timestamp,
        "is_owner": is_owner,
        "is_recruit": is_recruit,
        "status": status,
        "requestable": requestable,
        "is_requested": is_requested,
        "comments": comments
    }

    return render(request, 'post.html', context)


#Comment
@login_required(login_url="/login")
def web_comment(request, post_id):
    post = Post.objects.filter(post_id=post_id).first()
    
    if not post:
        return render(request, 'pagenotfound.html', status=404)

    if request.method == 'POST':
        comment = request.POST.get('comment').strip() 

        if comment: 
            PostComment.objects.create(
                post=post,
                user=request.user,
                comment=comment,
                reaction=""
            )

        else:
            messages.error(request, 'Please input something')

    return redirect(f'/post/{post_id}')


#Toggle-Status
@login_required(login_url="/login")
def toggle_status(request, post_id):
    user = request.user
    post = Post.objects.filter(post_id=post_id, user=user).first()

    if not post:
        return render(request, 'pagenotfound.html', status=404)

    recruit = RecruitPost.objects.get(post=post)
    recruit.status = not recruit.status
    recruit.save()
    
    return redirect(f'/post/{post_id}')


#Create Post
@login_required(login_url="/login")
def create_post(request):
    request.session['visited_create'] = False
    tag_list = [tag.name for tag in Tag.objects.all()]

    if request.method == 'POST':
        heading = request.POST.get('heading')
        content = request.POST.get('content')
        amount = int(request.POST.get('amount'))
        tags = [tag.strip() for tag in request.POST.get('tags').split(',') if tag.strip()]
        invalid = False

        if not heading.strip():
            invalid = True
            messages.error(request, 'Please enter heading')

        if not content.strip():
            invalid = True
            messages.error(request, 'Please enter content')

        if amount > 50 or amount < 1:
            invalid = True
            messages.error(request, 'Can recruit 1 to 50')    

        if len(tags) > 3:
            invalid = True
            messages.error(request, 'Only 3 tags can use')

        if invalid:
            context = {
                "heading": heading,
                "content": content,
                "amount": amount,
                "tags": request.POST.get('tags'),
                "tag_list": tag_list,
            }

            return render(request, 'create.html', context)

        request.session['heading'] = heading
        request.session['content'] = content
        request.session['amount'] = amount
        request.session['tags'] = tags
        request.session['visited_create'] = True

        return redirect('/create/requirement')

    return render(request, 'create.html', {"tag_list": tag_list})


#Requirement
@login_required(login_url="/login")
def web_requirement(request):
    user = request.user
    heading = request.session.get('heading')
    content = request.session.get('content')
    amount = request.session.get('amount')
    tags = request.session.get('tags')

    faculty_list = [faculty.name for faculty in Faculty.objects.all()]
    major_list = [major.name for major in Major.objects.all()]

    context = {
        "faculty_list": faculty_list,
        "major_list": major_list
    }

    if request.method == 'POST' and request.session.get('visited_create'):
        req_faculty = [faculty.strip() for faculty in request.POST.get('req_faculty').split(',') if faculty.strip()]
        req_major = [major.strip() for major in request.POST.get('req_major').split(',') if major.strip()]
        min_year = int(request.POST.get('min_year'))
        max_year = int(request.POST.get('max_year'))
        description = request.POST.get('description')
        invalid = False

        if len(req_faculty) == 0:
            req_faculty = ["Any"]

        if len(req_major) == 0:
            req_major = ["Any"]

        if min_year > max_year:
            invalid = True
            messages.error(request, 'min <= max')

        if not description.strip():
            invalid = True
            messages.error(request, 'Put something in description')

        if invalid:
            context = {
                "req_faculty": request.POST.get('req_faculty'),
                "req_major": request.POST.get('req_major'),
                "description": request.POST.get('description'),
                "faculty_list": faculty_list,
                "major_list": major_list
            }

            return render(request, 'requirement.html', context)

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
            year_min=min_year,
            year_max=max_year,
            description=description
        )
        requirement.req_faculty.set(req_faculty)
        requirement.req_major.set(req_major)
        requirement.save()

        team = Team.objects.create(team_leader=user, recruit_post=post)        
        TeamMember.objects.create(team=team, member=user)

        chat_group = ChatGroup.objects.create(
            team=team,
            admin=user,
        )
        chat_group.members.add(user)
        chat_group.save()

        request.session['visited_create'] = False

        return redirect('/recruitment')
    
    elif not request.session.get('visited_create'):
        return redirect('/create')

    return render(request, 'requirement.html', context)


#Request
@login_required(login_url="/login")
def web_request(request, post_id):
    if request.method == 'POST' and is_requestable(request.user, post_id):
        message = "ต้องการเข้าร่วมทีม"
        form = RequestMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
        
        user = request.user
        post = Post.objects.get(post_id=post_id)
        requirement = Requirement.objects.get(
            post=RecruitPost.objects.get(post=post)
        )

        a_request = Request.objects.create(
            post=post,
            user=user,
            message=message,
            requirement=requirement
        )
        a_request.save()

        return redirect(f'/post/{post_id}')
    
    return redirect('/')


#Team
@login_required(login_url="/login")
def teams(request):
    user = request.user
    active = Team.objects.filter(
        Q(teammember__member=user),
        recruit_post__finish=False
    ).distinct()
    finished = Team.objects.filter(
        Q(teammember__member=user),
        recruit_post__finish=True
    ).distinct()
    
    context = {
        "user": user,
        "active": active,
        "finished": finished
    }

    return render(request, 'teams.html', context)

@login_required(login_url="/login")
def team(request, team_id):
    user = request.user
    team = Team.objects.get(team_id=team_id)
    members = [
        teammember.member for teammember in TeamMember.objects.filter(team=team)
    ]
    
    if user not in members:
        return render(request, 'pagenotfound.html', status=404)

    is_owner = team.team_leader == user
    is_finish = team.recruit_post.finish

    request_list = list(Request.objects.filter(post=team.recruit_post)) if is_owner else []
    
    context = {
        "team_id": team_id,
        "members": members,
        "is_owner": is_owner,
        "is_finish": is_finish,
        "request_list": request_list
    }

    return render(request, 'team.html', context)


#Accept
@login_required(login_url="/login")
def accept(request, request_id):
    user = request.user
    req = Request.objects.filter(request_id=request_id).first()

    if (not req):
        return render(request, 'pagenotfound.html', status=404)

    post = req.post

    if user != post.user:
        return render(request, 'pagenotfound.html', status=404)
    
    team = Team.objects.get(recruit_post=post)
    TeamMember.objects.create(
        team=team,
        member=req.user
    )

    chat_group = ChatGroup.objects.filter(team=team).first()
    chat_group.members.add(req.user)

    return redirect(f'/team/{team.team_id}')


#Finish
@login_required(login_url="/login")
def finish(request, team_id, is_post_result):
    user = request.user
    team = Team.objects.filter(team_id=team_id).first()
    is_post_result = is_post_result.lower()

    if (not team) or (user != team.team_leader) or (is_post_result not in ['yes', 'no']):
        return render(request, 'pagenotfound.html', status=404)

    post = team.recruit_post
    post.finish = True
    post.save()

    recruit = RecruitPost.objects.filter(post=post).first()
    recruit.status = False
    recruit.save()

    if is_post_result == 'yes':
        return redirect(f'/post_result/{post.post_id}')
    
    return redirect(f'/team/{team_id}')


#Post result
@login_required(login_url="/login")
def post_result(request, post_id):
    post = Post.objects.filter(post_id=post_id).first()
    result_post = ResultPost.objects.filter(post=post).first()
    tag_list = [tag.name for tag in Tag.objects.all()]

    if (not post) or result_post or (not post.finish) or (post.user != request.user):
        return render(request, 'pagenotfound.html', status=404)

    if request.method == 'POST':
        heading = request.POST.get('heading').strip()
        content = request.POST.get('content').strip()
        tags = [tag.strip() for tag in request.POST.get('tags').split(',') if tag.strip()]

        if (not heading) or (not content) or (len(tags) == 0):
            context = {
                "heading": heading,
                "content": content,
                "tag_list": tag_list,
            }

            messages.error(request, 'Must fill every field')

            return render(request, 'post_result.html', context)

        post.heading = heading
        post.content = content
        post.save()

        result_post = ResultPost.objects.create(
            post=post,
            tag=tags
        )
        result_post.save()

        return redirect('/result')

    context = {
        "heading": post.heading,
        "content": post.content,
        "tag_list": tag_list,
    }

    return render(request, 'post_result.html', context)


#Feedback
@login_required(login_url="/login")
def feedback(request, team_id):
    user = request.user
    team = Team.objects.filter(team_id=team_id).first()
    members = [member.member for member in TeamMember.objects.filter(team=team) if member.member != user]
    feedback_forms = {}

    is_join_team = TeamMember.objects.filter(team=team, member=user).first()
    is_finish = team.recruit_post.finish if team else False
    is_feedbacked = Feedback.objects.filter(team=team).first() #in case that only feedback 1 user

    if (not is_finish) or (not is_join_team) or (not team) or is_feedbacked:
        return render(request, 'pagenotfound.html', status=404)

    if request.method == 'POST':
        for member in members:
            form = FeedbackForm(request.POST, prefix=f"feedback_{member.username}")
            if form.is_valid():
                feedback = Feedback.objects.create(
                    reviewer=user,
                    receiver=member,
                    team=team,
                    communication_pt=form.cleaned_data['communication_pt'],
                    collaboration_pt=form.cleaned_data['collaboration_pt'],
                    reliability_pt=form.cleaned_data['reliability_pt'],
                    technical_pt=form.cleaned_data['technical_pt'],
                    empathy_pt=form.cleaned_data['empathy_pt'],
                    comment=form.cleaned_data['comment']
                )
                feedback.save()
                
        return redirect('/myaccount')
    
    for member in members:
        feedback_form = FeedbackForm(prefix=f"feedback_{member.username}")
        feedback_forms[member.username] = feedback_form

    context = {
        "user": user,
        "feedback_forms": feedback_forms,
        "members": members
    }

    return render(request, 'feedback.html', context)


#Search-recruit no search by requirement
def search_recruit(request):
    if request.method == "POST":
        search = request.POST.get('seacrh')

        if search.strip():
            search = [s.strip() for s in search.split(',') if s.strip()]
            query = Q()

            for tag in search:
                query |= Q(tag__name__icontains=tag)

            recruits = RecruitPost.objects.filter(query)

            posts = []
            for post in recruits:
                posts.append(post.post)

            context = {
                "posts": posts,
            }

            return render(request, 'recruitment.html', context)

    return redirect('/recruitment')


#Search-result
def search_result(request):
    if request.method == "POST":
        search = request.POST.get('seacrh')

        if search.strip():
            search = [s.strip() for s in search.split(',') if s.strip()]
            query = Q()

            for tag in search:
                query |= Q(tag__name__icontains=tag)

            results = ResultPost.objects.filter(query)

            posts = []
            for post in results:
                posts.append(post.post)

            context = {
                "posts": posts,
            }

            return render(request, 'result.html', context)

    return redirect('/result')


#Message
@login_required(login_url="/login")
def message_history(request, receiver):
    return render()


#Help
def help(request):
    return render(request, 'help.html')