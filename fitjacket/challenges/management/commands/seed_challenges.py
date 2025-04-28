from django.core.management.base import BaseCommand
from challenges.models import Challenge

class Command(BaseCommand):
    help = 'Seed initial challenges into the database'

    def handle(self, *args, **options):
        initial = [
            {'title': 'Run 5K', 'description': 'Complete a 5 kilometer run', 'difficulty': Challenge.MEDIUM, 'point_value': 20},
            {'title': 'Morning Yoga', 'description': 'Do a 30-minute yoga session', 'difficulty': Challenge.EASY,   'point_value': 10},
            {'title': 'HIIT Blast',    'description': 'Finish a 20-minute high-intensity interval training', 'difficulty': Challenge.HARD, 'point_value': 30},
            {'title': 'Cycle 10K',     'description': 'Complete a 10 kilometer cycling session', 'difficulty': Challenge.MEDIUM, 'point_value': 25},
            {'title': 'Swim 1K',       'description': 'Swim 1 kilometer in open water or pool', 'difficulty': Challenge.MEDIUM, 'point_value': 25},
            {'title': 'Push-up 100',   'description': 'Perform 100 push-ups in a single session', 'difficulty': Challenge.HARD,   'point_value': 30},
            {'title': 'Plank 5 Minutes','description': 'Hold a plank position for 5 minutes', 'difficulty': Challenge.HARD,  'point_value': 30},
            {'title': '10K Steps',     'description': 'Walk at least 10,000 steps', 'difficulty': Challenge.EASY,  'point_value': 15},
            {'title': 'Dance 30 Minutes','description': 'Dance continuously for 30 minutes', 'difficulty': Challenge.MEDIUM,'point_value': 20},
        ]
        for data in initial:
            obj, created = Challenge.objects.update_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'difficulty': data['difficulty'],
                    'point_value': data['point_value'],
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f"{status}: {obj.title}")
        self.stdout.write(self.style.SUCCESS('All challenges seeded.'))