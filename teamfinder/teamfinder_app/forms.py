from django import forms
from .models import UserProfile, User
from teamfinder_app.models import Feedback, RecruitPost, ResultPost, Post
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from cloudinary.forms import CloudinaryFileField  


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "email_address", "name", "major", "faculty", "year")


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ("username", "email_address", "name", "major", "faculty", "year")


class RequestMessageForm(forms.Form):
    message = forms.CharField(max_length=200)

class ProfileImageUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image']

    profile_image = CloudinaryFileField(
    options = {
        'folder': 'images',
        'crop': 'limit', 'width': 600, 'height': 600,
        'quality': "auto:low"
    })

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = [
            'communication_pt',
            'collaboration_pt',
            'reliability_pt',
            'technical_pt',
            'empathy_pt',
            'comment'
        ]

    communication_pt = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    collaboration_pt = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    reliability_pt = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    technical_pt = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    empathy_pt = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect,
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )