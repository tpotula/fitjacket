from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from django.db import models

from .forms import LoginForm, SignupForm
from challenges.models import Participation
from workouts.models import WorkoutLog, Meal
import datetime




def auth_home(request):
    return render(request, 'accounts/auth_home.html')


def login_view(request):
    form = LoginForm(request.POST or None)

    # Clear any old messages
    storage = get_messages(request)
    list(storage)  # Consume the iterator to clear it

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        level = form.cleaned_data['level']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.profile.level = level
            user.profile.save()
            login(request, user)
            return redirect('dashboard')
    return render(request, 'accounts/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('auth_home')


class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password")
        password2 = cleaned_data.get("confirm_password")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


def reset_password_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not username or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
        elif new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                user = User.objects.get(username=username)
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "Password reset successfully. Please log in.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
    return render(request, 'accounts/reset_password.html')


@login_required
def dashboard_view(request):
    profile = request.user.profile
    ongoing_challenges = Participation.objects.filter(
        user=request.user,
        completed_at__isnull=True
    )
    today = datetime.date.today()
    first_day = today.replace(day=1)
    workouts_count = WorkoutLog.objects.filter(
        user=request.user,
        date__gte=first_day,
        date__lte=today
    ).count()
    monthly_goal = 15
    progress_percent = int(workouts_count / monthly_goal * 100) if monthly_goal else 0
    if progress_percent > 100:
        progress_percent = 100

    # --- Google Charts Data ---
    days = 7
    date_list = [(today - datetime.timedelta(days=x)) for x in range(days-1, -1, -1)]
    date_strs = [d.strftime('%Y-%m-%d') for d in date_list]

    # Workouts per day (last 7 days)
    workout_data = (
        WorkoutLog.objects.filter(user=request.user, date__gte=date_list[0], date__lte=date_list[-1])
        .values('date')
        .annotate(count=models.Count('id'), duration=models.Sum('duration'))
    )
    workout_dict = {d: {'count': 0, 'duration': 0} for d in date_strs}
    for entry in workout_data:
        key = entry['date'].strftime('%Y-%m-%d')
        workout_dict[key] = {
            'count': entry['count'],
            'duration': entry['duration'] or 0
        }
    workout_chart = [['Date', 'Workouts', 'Duration']]
    for d in date_strs:
        workout_chart.append([d, workout_dict[d]['count'], workout_dict[d]['duration']])

    # Calories per day (last 7 days)
    meal_data = (
        Meal.objects.filter(user=request.user, date__gte=date_list[0], date__lte=date_list[-1])
        .values('date')
        .annotate(calories=models.Sum('calories'))
    )
    meal_dict = {d: 0 for d in date_strs}
    for entry in meal_data:
        key = entry['date'].strftime('%Y-%m-%d')
        meal_dict[key] = entry['calories'] or 0
    meal_chart = [['Date', 'Calories']]
    for d in date_strs:
        meal_chart.append([d, meal_dict[d]])

    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'ongoing_challenges': ongoing_challenges,
        'monthly_goal': monthly_goal,
        'progress_percent': progress_percent,
        'workouts_count': workouts_count,
        'workout_chart': workout_chart,
        'meal_chart': meal_chart,
    })