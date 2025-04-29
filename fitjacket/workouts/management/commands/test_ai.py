from django.core.management.base import BaseCommand
import json
from workouts.ai_service import WorkoutAIService

class Command(BaseCommand):
    help = 'Test the AI service functionality'

    def handle(self, *args, **options):
        try:
            # Initialize the service
            self.stdout.write('Initializing AI service...')
            service = WorkoutAIService()
            
            # Test workout plan generation
            self.stdout.write('\nTesting workout plan generation...')
            plan = service.generate_workout_plan(
                user_level='beginner',
                recent_workouts='push-ups, squats',
                equipment='dumbbells, resistance bands',
                duration=30,
                workout_type='strength'
            )
            self.stdout.write('\nGenerated Workout Plan:')
            self.stdout.write(json.dumps(plan, indent=2))
            
            # Test workout variation generation
            self.stdout.write('\nTesting workout variation generation...')
            variation = service.generate_workout_variation(
                user_level='beginner',
                recent_workouts='push-ups, squats',
                equipment='dumbbells, resistance bands'
            )
            self.stdout.write('\nGenerated Workout Variation:')
            self.stdout.write(json.dumps(variation, indent=2))
            
            # Test progression plan generation
            self.stdout.write('\nTesting progression plan generation...')
            progression = service.generate_progression_plan(
                exercise_name='push-ups',
                current_stats='can do 10 reps',
                user_level='beginner'
            )
            self.stdout.write('\nGenerated Progression Plan:')
            self.stdout.write(json.dumps(progression, indent=2))
            
        except Exception as e:
            self.stderr.write(f'Error during testing: {str(e)}') 