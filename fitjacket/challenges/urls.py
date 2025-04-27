from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('',          views.challenge_list, name='list'),
    path('join/<int:pk>/', views.join_challenge, name='join'),
    path('create/', views.create_challenge, name='create'),
    path(
        'participation/<int:participation_id>/complete/',
        views.complete_challenge,
        name='complete'
    ),
]