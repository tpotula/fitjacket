from django.db import models
from django.conf import settings

class Challenge(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField()
    start_date  = models.DateField()
    end_date    = models.DateField()

class Participation(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    challenge    = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    joined_at    = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
