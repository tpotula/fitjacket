from django.db import models
from django.conf import settings

class Challenge(models.Model):
    EASY = 'E'
    MEDIUM = 'M'
    HARD = 'H'
    DIFFICULTY_CHOICES = [
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=1,
        choices=DIFFICULTY_CHOICES,
        default=EASY,
    )
    point_value = models.PositiveIntegerField(
        default=10,
        help_text='Points awarded upon completion'
    )

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"

class Participation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    points_awarded = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Points earned at completion'
    )

    class Meta:
        unique_together = ('user', 'challenge')

    def __str__(self):
        return f"Participation of {self.user} in {self.challenge}"