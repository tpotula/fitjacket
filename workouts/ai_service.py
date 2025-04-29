import google.generativeai as genai
import json
import logging
import re

logger = logging.getLogger(__name__)

class WorkoutAIService:
    def __init__(self):
        try:
            # Log available models for debugging
            logger.info("Available models:")
            for m in genai.list_models():
                logger.info(f"Model: {m.name}")
            
            # Use a supported model from the available models list
            self.model = genai.GenerativeModel('gemini-2.0-flash-lite')
            
            # Configure generation parameters for more consistent output
            self.generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            logger.info("Successfully initialized Gemini AI model")
        except Exception as e:
            logger.error(f"Error initializing Gemini AI: {str(e)}")
            raise

    def _clean_json_response(self, text):
        """Clean and extract JSON from the model's response."""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            return None

    def _generate_with_retry(self, prompt, max_retries=3):
        """Generate content with retry logic and proper error handling."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
                
                if not response.text:
                    logger.error("Empty response from model")
                    continue
                    
                # Clean and parse the response
                result = self._clean_json_response(response.text)
                if result:
                    return result
                    
                logger.warning(f"Attempt {attempt + 1}: Invalid JSON response")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
        return None

    def generate_workout_plan(self, user_level, recent_workouts, equipment, duration, workout_type):
        try:
            # Create a prompt for the AI
            prompt = f"""
            You are an expert fitness trainer creating a personalized workout plan. Consider the following information:
            - User Level: {user_level}
            - Recent Workouts: {recent_workouts}
            - Available Equipment: {equipment}
            - Preferred Duration: {duration} minutes
            - Preferred Workout Type: {workout_type}

            Create a workout plan that:
            1. Is appropriate for the user's level
            2. Uses only the available equipment
            3. Fits within the specified duration
            4. Avoids exercises from recent workouts
            5. Includes proper warm-up and cool-down
            6. Has clear progression instructions

            Return ONLY a valid JSON object in this exact format, with no additional text:
            {{
                "title": "Creative and engaging workout title",
                "description": "Detailed description of the workout and its benefits",
                "duration": {duration},
                "difficulty": "{user_level}",
                "exercises": [
                    {{
                        "name": "Exercise Name",
                        "sets": number_of_sets,
                        "reps": "reps_description",
                        "notes": "Form tips and modifications"
                    }}
                ],
                "progression": "Clear progression plan with specific goals"
            }}
            """

            logger.info(f"Generating workout plan with prompt: {prompt}")
            
            # Generate response with retry logic
            workout_plan = self._generate_with_retry(prompt)
            
            if workout_plan:
                logger.info(f"Successfully generated workout plan: {workout_plan}")
                return workout_plan
                
            # Return default workout plan if AI fails
            logger.warning("Using default workout plan due to AI generation failure")
            return {
                "title": "Full Body Workout",
                "description": "A balanced workout targeting all major muscle groups.",
                "duration": int(duration) if duration else 45,
                "difficulty": user_level,
                "exercises": [
                    {
                        "name": "Push-ups",
                        "sets": 3,
                        "reps": "10-12",
                        "notes": "Keep your core tight and maintain proper form"
                    },
                    {
                        "name": "Squats",
                        "sets": 3,
                        "reps": "12-15",
                        "notes": "Keep your back straight and knees aligned with toes"
                    },
                    {
                        "name": "Plank",
                        "sets": 3,
                        "reps": "30 seconds",
                        "notes": "Maintain a straight line from head to heels"
                    }
                ],
                "progression": "Increase reps or duration by 10% each week"
            }
        except Exception as e:
            logger.error(f"Error generating workout plan: {str(e)}")
            raise

    def generate_workout_variation(self, user_level, recent_workouts, equipment):
        try:
            # Create a prompt for generating workout variations
            prompt = f"""
            You are an expert fitness trainer creating a workout variation. Consider the following information:
            - User Level: {user_level}
            - Recent Workouts: {recent_workouts}
            - Available Equipment: {equipment}

            Create a workout variation that:
            1. Is different from recent workouts
            2. Uses only the available equipment
            3. Maintains appropriate difficulty level
            4. Includes new exercises or variations
            5. Has clear progression instructions

            Return ONLY a valid JSON object in this exact format, with no additional text:
            {{
                "title": "Creative and engaging workout title",
                "description": "Detailed description of the workout and its benefits",
                "duration": 45,
                "difficulty": "{user_level}",
                "exercises": [
                    {{
                        "name": "Exercise Name",
                        "sets": number_of_sets,
                        "reps": "reps_description",
                        "notes": "Form tips and modifications"
                    }}
                ],
                "progression": "Clear progression plan with specific goals"
            }}
            """

            logger.info(f"Generating workout variation with prompt: {prompt}")
            
            # Generate response with retry logic
            workout_variation = self._generate_with_retry(prompt)
            
            if workout_variation:
                logger.info(f"Successfully generated workout variation: {workout_variation}")
                return workout_variation
                
            logger.error("Failed to generate workout variation")
            return None
        except Exception as e:
            logger.error(f"Error generating workout variation: {str(e)}")
            return None

    def generate_progression_plan(self, exercise_name, current_stats, user_level):
        try:
            # Create a prompt for generating progression plans
            prompt = f"""
            You are an expert fitness trainer creating a progression plan. Consider the following information:
            - Exercise: {exercise_name}
            - Current Stats: {current_stats}
            - User Level: {user_level}

            Create a progression plan that:
            1. Is appropriate for the user's level
            2. Provides clear next steps
            3. Includes safety considerations
            4. Has realistic timelines
            5. Includes alternative exercises if needed

            Return ONLY a valid JSON object in this exact format, with no additional text:
            {{
                "title": "Progression Plan for {exercise_name}",
                "description": "Detailed progression strategy",
                "duration": 30,
                "difficulty": "{user_level}",
                "exercises": [
                    {{
                        "name": "Exercise Name",
                        "sets": number_of_sets,
                        "reps": "reps_description",
                        "notes": "Form tips and modifications"
                    }}
                ],
                "progression": "Clear progression plan with specific goals"
            }}
            """

            logger.info(f"Generating progression plan with prompt: {prompt}")
            
            # Generate response with retry logic
            progression_plan = self._generate_with_retry(prompt)
            
            if progression_plan:
                logger.info(f"Successfully generated progression plan: {progression_plan}")
                return progression_plan
                
            logger.error("Failed to generate progression plan")
            return None
        except Exception as e:
            logger.error(f"Error generating progression plan: {str(e)}")
            return None 