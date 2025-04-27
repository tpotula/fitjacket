from django.db import models
from django.contrib.auth.models import User

class GuidedWorkout(models.Model):
    title = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=[("beginner", "Beginner"), ("athlete", "Athlete")])
    description = models.TextField()
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.level})"

class WorkoutLog(models.Model):
    WORKOUT_TYPE_CHOICES = [
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('flexibility', 'Flexibility'),
        ('balance', 'Balance'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES)
    exercise_name = models.CharField(max_length=100)
    sets = models.PositiveIntegerField(null=True, blank=True)
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)  # in minutes
    notes = models.TextField(blank=True)
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exercise_name} ({self.workout_type}) on {self.date}"