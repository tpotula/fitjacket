from django.core.management.base import BaseCommand
from workouts.ai_service import WorkoutAIService
import json

class Command(BaseCommand):
    help = 'Test the AI service functionality'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Initializing AI Service...')
            ai_service = WorkoutAIService()
            
            # Test workout plan generation
            self.stdout.write('\nTesting workout plan generation...')
            workout_plan = ai_service.generate_workout_plan(
                user_level="intermediate",
                recent_workouts=["chest day", "leg day"],
                equipment=["dumbbells", "resistance bands"],
                duration=45,
                workout_type="strength"
            )
            self.stdout.write(json.dumps(workout_plan, indent=2))
            
            # Test workout variation generation
            self.stdout.write('\nTesting workout variation generation...')
            variation = ai_service.generate_workout_variation(
                user_level="intermediate",
                recent_workouts=["chest day", "leg day"],
                equipment=["dumbbells", "resistance bands"]
            )
            self.stdout.write(json.dumps(variation, indent=2))
            
            # Test progression plan generation
            self.stdout.write('\nTesting progression plan generation...')
            progression = ai_service.generate_progression_plan(
                exercise_name="Push-ups",
                current_stats="3 sets of 10 reps",
                user_level="intermediate"
            )
            self.stdout.write(json.dumps(progression, indent=2))
            
        except Exception as e:
            self.stderr.write(f'Error: {str(e)}') 