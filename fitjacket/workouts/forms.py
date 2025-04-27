# workouts/forms.py

from django import forms
from .models import WorkoutLog, Meal, Injury

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