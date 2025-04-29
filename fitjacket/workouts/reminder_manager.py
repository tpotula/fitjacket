from django.utils import timezone
from .models import Reminder

def notify_user(func):
    """
    Decorator that adds user notification functionality to reminder methods
    """
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        if result and hasattr(result, 'remind_at'):
            time_diff = result.remind_at - timezone.now()
            if time_diff.total_seconds() <= 300:  # Within 5 minutes
                print(f"⏰ Upcoming reminder: {result.text}")
        return result
    return wrapper

class ReminderManager:
    """
    Singleton pattern for managing reminders across the application
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @notify_user
    def get_next_reminder(self, user):
        """Get the next upcoming reminder for a user"""
        return Reminder.objects.filter(
            user=user,
            completed=False,
            remind_at__gte=timezone.now()
        ).order_by('remind_at').first()

    def get_imminent_reminders(self, user):
        """Get all reminders within next 10 minutes"""
        now = timezone.localtime(timezone.now())  # Get the current time in local timezone
        ten_mins_later = now + timezone.timedelta(minutes=10)
        
        return Reminder.objects.filter(
            user=user,
            completed=False,
            remind_at__gt=now,
            remind_at__lte=ten_mins_later
        ).order_by('remind_at')

    def get_all_reminders(self, user):
        """Get all upcoming reminders for a user"""
        return Reminder.objects.filter(
            user=user,
            completed=False
        ).order_by('remind_at')

    def mark_complete(self, reminder_id, user):
        """Mark a reminder as complete"""
        reminder = Reminder.objects.get(id=reminder_id, user=user)
        reminder.completed = True
        reminder.save()
        return reminder 