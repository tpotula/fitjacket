from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def auth_home(request):
    return render(request, 'accounts/auth_home.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Replace with your post-login page
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        level = request.POST['level']  # 'beginner' or 'athlete'
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.profile.level = level  # Assuming you add this field to a Profile model later
            user.profile.save()
            login(request, user)
            return redirect('dashboard')
    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    return redirect('auth_home')

@login_required
def dashboard_view(request):
    profile = request.user.profile
    return render(request, 'accounts/dashboard.html', {'profile': profile})
