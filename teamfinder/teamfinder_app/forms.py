from django import forms
from .models import UserProfile, User
from teamfinder_app.models import Feedback, RecruitPost
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


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

class RecruitPostEditForm(forms.ModelForm):
    heading = forms.CharField(max_length=255)  # From Post model
    content = forms.CharField(widget=forms.Textarea)  # From Post model

    class Meta:
        model = RecruitPost
        fields = ['tag']  # From RecruitPost model

    def __init__(self, *args, **kwargs):
        # Fetch related Post instance data
        post_instance = kwargs.pop('post_instance', None)
        super().__init__(*args, **kwargs)

        if post_instance:
            # Pre-fill fields with Post data
            self.fields['heading'].initial = post_instance.heading
            self.fields['content'].initial = post_instance.content

    def save(self, post_instance=None, commit=True):
        # Save changes to Post model
        if post_instance:
            post_instance.heading = self.cleaned_data['heading']
            post_instance.content = self.cleaned_data['content']
            if commit:
                post_instance.save()

        # Save changes to RecruitPost model
        return super().save(commit=commit)
