from django.db.models.signals import post_save
from django.dispatch        import receiver
from .models                import WorkoutLog
from accounts.models        import Profile
from django.db.models       import F

@receiver(post_save, sender=WorkoutLog)
def award_workout_points(sender, instance, created, **kwargs):
    print(f"Signal: WorkoutLog saved for {instance.user.username}, created={created}")
    if created:
        Profile.objects.filter(user=instance.user).update(points=F('points')+5)
        print(" → Awarded 5 points")