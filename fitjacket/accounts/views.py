from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .forms import LoginForm, SignupForm
from django.contrib.messages import get_messages




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

@login_required
def dashboard_view(request):
    profile = request.user.profile
    return render(request, 'accounts/dashboard.html', {'profile': profile})

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
    return render(request, 'accounts/dashboard.html', {'profile': profile})
