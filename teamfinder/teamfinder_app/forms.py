from django import forms
from .models import UserProfile

class RequestMessageForm(forms.Form):
    message = forms.CharField(max_length=200)

class ImageUploadForm(forms.Form):
    class Meta:
        model = UserProfile
        fields = ['profile_image']