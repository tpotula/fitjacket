import os
import sys
import django
import json

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitjacket.settings')
django.setup()

from fitjacket.workouts.ai_service import WorkoutAIService

def test_workout_generation():
    try:
        # Initialize the service
        service = WorkoutAIService()
        
        # Test workout plan generation
        print("\nTesting workout plan generation...")
        plan = service.generate_workout_plan(
            user_level='beginner',
            recent_workouts='push-ups, squats',
            equipment='dumbbells, resistance bands',
            duration=30,
            workout_type='strength'
        )
        print("\nGenerated Workout Plan:")
        print(json.dumps(plan, indent=2))
        
        # Test workout variation generation
        print("\nTesting workout variation generation...")
        variation = service.generate_workout_variation(
            user_level='beginner',
            recent_workouts='push-ups, squats',
            equipment='dumbbells, resistance bands'
        )
        print("\nGenerated Workout Variation:")
        print(json.dumps(variation, indent=2))
        
        # Test progression plan generation
        print("\nTesting progression plan generation...")
        progression = service.generate_progression_plan(
            exercise_name='push-ups',
            current_stats='can do 10 reps',
            user_level='beginner'
        )
        print("\nGenerated Progression Plan:")
        print(json.dumps(progression, indent=2))
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == '__main__':
    test_workout_generation() 