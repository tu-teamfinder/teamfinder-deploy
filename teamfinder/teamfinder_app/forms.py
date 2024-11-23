from django import forms
from .models import UserProfile

class RequestMessageForm(forms.Form):
    message = forms.CharField(max_length=200)

class ProfileImageUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image']