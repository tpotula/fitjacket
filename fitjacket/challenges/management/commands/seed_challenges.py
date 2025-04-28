from django.core.management.base import BaseCommand
from challenges.models import Challenge

class Command(BaseCommand):
    help = 'Seed initial challenges into the database'

    def handle(self, *args, **options):
        initial = [
            {
                'title': 'Run 5K',
                'description': 'Complete a 5 kilometer run',
                'difficulty': Challenge.MEDIUM,
                'point_value': 20,
            },
            {
                'title': 'Morning Yoga',
                'description': 'Do a 30-minute yoga session',
                'difficulty': Challenge.EASY,
                'point_value': 10,
            },
            {
                'title': 'HIIT Blast',
                'description': 'Finish a 20-minute high-intensity interval training',
                'difficulty': Challenge.HARD,
                'point_value': 30,
            },
        ]
        for data in initial:
            obj, created = Challenge.objects.update_or_create(
                title=data['title'],
                defaults=data
            )
            verb = 'Created' if created else 'Updated'
            self.stdout.write(f"{verb} challenge: {obj.title}")
        self.stdout.write(self.style.SUCCESS('Seeding complete.'))