from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=10, choices=[('beginner', 'Beginner'), ('athlete', 'Athlete')])
    joined_challenges = models.ManyToManyField(
        'challenges.Challenge',
        blank=True,
        related_name='participants'
    )
