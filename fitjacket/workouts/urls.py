# workouts/urls.py
from django.urls import path
from . import views

app_name = 'workouts'

urlpatterns = [
    path('', views.workouts_home_view, name='workouts_home'),
    path('guided/', views.guided_workouts_view, name='guided_workouts'),
    path('log/', views.workout_log_view, name='workout_log'),
    path('nutrition/', views.nutrition_tracking_view, name='nutrition_tracking'),
    path('nutrition/add/', views.add_meal_view, name='add_meal'),
    path('injuries/', views.injury_log_view, name='injury_log'),
    path('injuries/toggle/<int:injury_id>/', views.toggle_injury_status, name='toggle_injury'),
    path('reminders/', views.reminders_view, name='reminders'),
    path('reminders/complete/<int:reminder_id>/', views.complete_reminder, name='complete_reminder'),
    path('analytics/', views.performance_analytics_view, name='performance_analytics'),
    path('ai-recommendations/', views.ai_recommendations_view, name='ai_recommendations'),
]
