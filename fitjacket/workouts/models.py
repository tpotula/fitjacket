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

class Reminder(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    text        = models.CharField(max_length=200)
    remind_at   = models.DateTimeField()
    completed   = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} at {self.remind_at}"

class Meal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    calories = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.meal_type}) on {self.date}"

class Injury(models.Model):
    BODY_PART_CHOICES = [
        ('neck', 'Neck'),
        ('shoulder', 'Shoulder'),
        ('upper_back', 'Upper Back'),
        ('lower_back', 'Lower Back'),
        ('chest', 'Chest'),
        ('arm', 'Arm'),
        ('elbow', 'Elbow'),
        ('wrist', 'Wrist'),
        ('hip', 'Hip'),
        ('thigh', 'Thigh'),
        ('knee', 'Knee'),
        ('ankle', 'Ankle'),
        ('foot', 'Foot'),
        ('other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body_part = models.CharField(max_length=20, choices=BODY_PART_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    description = models.TextField()
    date_logged = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    recovery_recommendations = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_body_part_display()} injury ({self.get_severity_display()})"

    def save(self, *args, **kwargs):
        # Generate recovery recommendations based on body part and severity
        recommendations = []
        
        if self.severity == 'severe':
            recommendations.append(f"Avoid any exercises involving the {self.get_body_part_display()}.")
            recommendations.append("Consult with a healthcare professional before resuming exercise.")
        elif self.severity == 'moderate':
            recommendations.append(f"Limit exercises involving the {self.get_body_part_display()}.")
            recommendations.append("Focus on gentle stretching and mobility exercises.")
        else:  # mild
            recommendations.append(f"Be cautious with exercises involving the {self.get_body_part_display()}.")
            recommendations.append("Consider reducing weight or intensity for affected exercises.")

        # Add specific recommendations based on body part
        if self.body_part in ['neck', 'upper_back', 'lower_back']:
            recommendations.append("Focus on core strengthening exercises.")
            recommendations.append("Maintain proper posture during all activities.")
        elif self.body_part in ['shoulder', 'elbow', 'wrist']:
            recommendations.append("Include shoulder mobility exercises.")
            recommendations.append("Consider using lighter weights or resistance bands.")
        elif self.body_part in ['hip', 'knee', 'ankle']:
            recommendations.append("Focus on low-impact exercises like swimming or cycling.")
            recommendations.append("Include balance and stability exercises.")

        self.recovery_recommendations = "\n".join(recommendations)
        super().save(*args, **kwargs)

class WorkoutPlan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    start_date = models.DateField()
    current_day = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.plan_type} Plan (Day {self.current_day})"

class WorkoutPlanDay(models.Model):
    plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()
    workout_type = models.CharField(max_length=20, choices=WorkoutLog.WORKOUT_TYPE_CHOICES)
    exercises = models.JSONField()  # Stores exercise details as JSON
    duration = models.PositiveIntegerField()  # in minutes
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['plan', 'day_number']
        ordering = ['day_number']
    
    def __str__(self):
        return f"Day {self.day_number} - {self.workout_type}"

class WorkoutProgression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise_name = models.CharField(max_length=100)
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    current_reps = models.PositiveIntegerField(null=True, blank=True)
    current_sets = models.PositiveIntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'exercise_name']
    
    def __str__(self):
        return f"{self.user.username}'s {self.exercise_name} Progression"
