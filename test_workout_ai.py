import os
import google.generativeai as genai
from workouts.ai_service import WorkoutAIService

def main():
    # Set up the API key
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set")
        return
    
    # Configure the API
    genai.configure(api_key=api_key)
    
    # Initialize the service
    service = WorkoutAIService()
    
    # Test parameters
    user_level = "intermediate"
    recent_workouts = ["Full Body Workout", "Upper Body Focus"]
    equipment = ["dumbbells", "resistance bands"]
    duration = 45
    workout_type = "strength"
    
    # Generate a workout plan
    workout_plan = service.generate_workout_plan(
        user_level=user_level,
        recent_workouts=recent_workouts,
        equipment=equipment,
        duration=duration,
        workout_type=workout_type
    )
    
    # Print the result
    print("\nGenerated Workout Plan:")
    print("======================")
    print(f"Title: {workout_plan['title']}")
    print(f"Description: {workout_plan['description']}")
    print(f"Duration: {workout_plan['duration']} minutes")
    print(f"Difficulty: {workout_plan['difficulty']}")
    print("\nExercises:")
    for exercise in workout_plan['exercises']:
        print(f"\n- {exercise['name']}")
        print(f"  Sets: {exercise['sets']}")
        print(f"  Reps: {exercise['reps']}")
        print(f"  Notes: {exercise['notes']}")
    print(f"\nProgression: {workout_plan['progression']}")

if __name__ == "__main__":
    main() 