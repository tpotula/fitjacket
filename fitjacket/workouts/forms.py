# workouts/forms.py

from django import forms
from .models import WorkoutLog, Meal, Injury, Reminder
from django.utils import timezone

class WorkoutLogForm(forms.ModelForm):
    class Meta:
        model = WorkoutLog
        fields = ['workout_type', 'exercise_name', 'sets', 'reps', 'weight', 'duration', 'notes', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'workout_type': forms.Select(attrs={'class': 'form-select'}),
            'exercise_name': forms.TextInput(attrs={'class': 'form-control'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control'}),
            'reps': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['meal_type', 'name', 'calories', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'meal_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What did you eat? (e.g., 2 eggs, toast, coffee)'}),
        }

class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = ['body_part', 'severity', 'description']
        widgets = {
            'body_part': forms.Select(attrs={'class': 'form-select'}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your injury in detail...'}),
        }

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['text', 'remind_at']
        widgets = {
            'text':      forms.TextInput(attrs={'class':'form-control', 'placeholder':'e.g. Workout at 6 PM'}),
            'remind_at': forms.DateTimeInput(attrs={'type':'datetime-local','class':'form-control'}),
        }
    
    def clean_remind_at(self):
        remind_at = self.cleaned_data['remind_at']
        if remind_at:
            # Check if the datetime is already timezone aware
            if timezone.is_naive(remind_at):
                # Only make it aware if it's naive
                return timezone.make_aware(remind_at)
            return remind_at
        return remind_at
