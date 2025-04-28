from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.messages import get_messages
from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render, redirect
import datetime

from .forms import LoginForm, SignupForm
from challenges.models import Participation
from workouts.models import WorkoutLog, Meal


def auth_home(request):
    """
    Optional landing page at /auth/.
    """
    return render(request, 'accounts/auth_home.html')


def login_view(request):
    """
    Display login form and authenticate users.
    """
    form = LoginForm(request.POST or None)
    # clear any prior messages
    storage = get_messages(request)
    list(storage)

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
    """
    Display signup form, register new users, and set their profile level.
    """
    form = SignupForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        level    = form.cleaned_data['level']
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
    """
    Log the user out.
    """
    logout(request)
    return redirect('auth_home')


class PasswordResetForm(forms.Form):
    """
    Simple form to reset a user's password by username.
    """
    new_password     = forms.CharField(widget=forms.PasswordInput, label="New password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def clean(self):
        cleaned = super().clean()
        pw1 = cleaned.get("new_password")
        pw2 = cleaned.get("confirm_password")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


def reset_password_view(request):
    """
    Handle password reset requests.
    """
    if request.method == 'POST':
        username         = request.POST.get('username', '').strip()
        new_password     = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not (username and new_password and confirm_password):
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

    return render(request, 'accounts/reset_password.html', {
        'form': PasswordResetForm()
    })


@login_required
def dashboard_view(request):
    """
    Render the dashboard, tracking:
      - ongoing challenges
      - total points (workouts + challenges)
      - dynamic next_goal achievements at 100-point increments
      - workout count and progress toward monthly goal
      - chart data
    """
    profile = request.user.profile

    # Sum completed-challenge points
    challenge_points = Participation.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).aggregate(
        total=Coalesce(Sum('points_awarded'), Value(0))
    )['total'] or 0

    # Combine with workout-earned points
    total_points = profile.points + challenge_points

    # Check & bump achievement milestone
    if total_points >= profile.next_goal:
        messages.success(
            request,
            f"🎉 Congrats! You reached {profile.next_goal} points. "
            f"New goal: {profile.next_goal + 100} points!"
        )
        profile.next_goal += 100
        profile.save()

    # Ongoing challenges
    ongoing_challenges = Participation.objects.filter(
        user=request.user,
        completed_at__isnull=True
    )

    # Monthly workout progress
    today      = datetime.date.today()
    first_day  = today.replace(day=1)
    workouts_count = WorkoutLog.objects.filter(
        user=request.user,
        date__gte=first_day,
        date__lte=today
    ).count()
    monthly_goal     = 15
    progress_percent = int(workouts_count / monthly_goal * 100) if monthly_goal else 0
    if progress_percent > 100:
        progress_percent = 100

    # Prepare chart data (last 7 days)
    days      = 7
    date_list = [today - datetime.timedelta(days=i) for i in range(days-1, -1, -1)]
    date_strs = [d.strftime('%Y-%m-%d') for d in date_list]

    workout_data = (
        WorkoutLog.objects.filter(user=request.user, date__in=date_list)
        .values('date')
        .annotate(count=models.Count('id'), duration=models.Sum('duration'))
    )
    workout_dict = {d: {'count':0,'duration':0} for d in date_strs}
    for e in workout_data:
        key = e['date'].strftime('%Y-%m-%d')
        workout_dict[key] = {'count':e['count'], 'duration':e['duration'] or 0}
    workout_chart = [['Date','Workouts','Duration']]
    for d in date_strs:
        workout_chart.append([d, workout_dict[d]['count'], workout_dict[d]['duration']])

    meal_data = (
        Meal.objects.filter(user=request.user, date__in=date_list)
        .values('date')
        .annotate(calories=models.Sum('calories'))
    )
    meal_dict = {d:0 for d in date_strs}
    for e in meal_data:
        key = e['date'].strftime('%Y-%m-%d')
        meal_dict[key] = e['calories'] or 0
    meal_chart = [['Date','Calories']]
    for d in date_strs:
        meal_chart.append([d, meal_dict[d]])

    # Build achievements milestones
    milestone_count = total_points // 100
    emoji_map = {1:'🥉',2:'🥈',3:'🥇',4:'🏆',5:'🌟'}
    milestones = [
        {'milestone': i*100, 'emoji': emoji_map.get(i, '🔱')}
        for i in range(1, milestone_count+1)
    ]
    achievement_progress = int(total_points / profile.next_goal * 100) if profile.next_goal else 0
    if achievement_progress > 100:
        achievement_progress = 100

    return render(request, 'accounts/dashboard.html', {
        'profile':              profile,
        'ongoing_challenges':   ongoing_challenges,
        'total_points':         total_points,
        'milestones':           milestones,
        'next_goal':            profile.next_goal,
        'achievement_progress': achievement_progress,
        'monthly_goal':         monthly_goal,
        'progress_percent':     progress_percent,
        'workouts_count':       workouts_count,
        'workout_chart':        workout_chart,
        'meal_chart':           meal_chart,
    })


@login_required
def achievements_view(request):
    """
    Standalone achievements page: uses same total_points logic.
    """
    profile = request.user.profile

    challenge_points = Participation.objects.filter(
        user=request.user,
        completed_at__isnull=False
    ).aggregate(
        total=Coalesce(Sum('points_awarded'), Value(0))
    )['total'] or 0

    total_points = profile.points + challenge_points

    milestone_count = total_points // 100
    emoji_map = {1:'🥉',2:'🥈',3:'🥇',4:'🏆',5:'🌟'}
    milestones = [
        {'milestone': i*100, 'emoji': emoji_map.get(i, '🔱')}
        for i in range(1, milestone_count+1)
    ]
    progress = int(total_points / profile.next_goal * 100) if profile.next_goal else 0

    return render(request, 'accounts/achievements.html', {
        'total_points': total_points,
        'milestones':   milestones,
        'next_goal':    profile.next_goal,
        'progress':     progress,
    })
