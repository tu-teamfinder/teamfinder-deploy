from django.contrib import admin

# Register your models here.
from django.apps import apps
from .models import *  # Import your models

# Dynamically register all models from your app
app = apps.get_app_config('teamfinder_app')  # Replace with your app's name
for model in app.get_models():
    admin.site.register(model)