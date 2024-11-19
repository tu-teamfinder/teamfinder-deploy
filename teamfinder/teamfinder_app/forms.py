from django import forms

class RequestMessageForm(forms.Form):
    message = forms.CharField(max_length=200)