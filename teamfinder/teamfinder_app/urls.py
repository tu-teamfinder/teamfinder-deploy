from django.urls import path
from teamfinder_app import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('about', views.about, name='about'),
    path('login', views.web_login, name='login'),
    path('logout', views.web_logout, name='logout'),
    path('myaccount', views.myaccount, name='myaccount'),
    path('create', views.create_post, name='create'),
    path('create/requirement', views.web_requirement, name='requirement'),
    path('post/<post_id>', views.web_post, name='post'),
    path('request/<post_id>', views.web_request, name='request'),
    path('recruitment', views.recruitment, name='recruitment'),
    path('result', views.result, name='result'),
    path('teams', views.teams, name='teams'),
    path('team/<team_id>', views.team, name='team'),
    path('finish/<team_id>/<is_post_result>', views.finish, name='finish'),
    path('post_result/<post_id>', views.post_result, name='post_result'),
    path('feedback/<team_id>', views.feedback, name='feedback'),
    path('recruitment/search', views.search_recruit, name='search_recruit'),
    path('result/search', views.search_result, name='search_result'),
    path('comment/<post_id>', views.web_comment, name='comment'),
    path('help', views.help, name='help'),
    path('mystats', views.my_stats, name='mystats')
]