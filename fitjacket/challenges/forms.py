from django import forms
from .models import Challenge

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        # only include valid Challenge fields
        fields = ['title', 'description', 'difficulty', 'point_value']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'difficulty': forms.Select(),
            'point_value': forms.NumberInput(attrs={'min': 0}),
        }