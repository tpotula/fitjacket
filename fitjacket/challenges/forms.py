from django import forms
from .models import Challenge

class ChallengeForm(forms.ModelForm):
    class Meta:
        model  = Challenge
        fields = ['title', 'description', 'start_date', 'end_date']