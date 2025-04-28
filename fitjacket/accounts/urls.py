from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth_home, name='auth_home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/achievements/', views.achievements_view, name='achievements'),
]
