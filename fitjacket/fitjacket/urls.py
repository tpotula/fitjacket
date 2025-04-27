from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect  # <-- Add this line

urlpatterns = [
    path('', lambda request: redirect('auth_home')),  # <-- Add this line
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('workouts/', include('workouts.urls')),
    path('challenges/', include('challenges.urls', namespace='challenges')),
]
