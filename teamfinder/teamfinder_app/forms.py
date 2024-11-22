from django import forms
from teamfinder_app.models import Feedback

class RequestMessageForm(forms.Form):
    message = forms.CharField(max_length=200)

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