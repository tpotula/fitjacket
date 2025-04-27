# workouts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.workouts_home_view, name='workouts_home'),
    path('guided/', views.guided_workouts_view, name='guided_workouts'),
    path('log/', views.workout_log_view, name='workout_log'),
]
