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
    path('recruitment', views.recruitment, name='recruitment'),
]