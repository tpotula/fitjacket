import google.generativeai as genai
from django.conf import settings
import json
import logging
import re
import os

logger = logging.getLogger(__name__)

class WorkoutAIService:
    def __init__(self):
        try:
            # Configure the API key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            
            genai.configure(api_key=api_key)
            
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
                try:
                    # First try direct JSON parsing
                    result = json.loads(response.text)
                    if result:
                        return result
                except json.JSONDecodeError:
                    # If direct parsing fails, try to extract and clean JSON
                    json_match = re.search(r'\{[\s\S]*\}', response.text)
                    if json_match:
                        try:
                            json_str = json_match.group(0)
                            
                            # Clean up JSON string
                            # Remove any text before the first {
                            json_str = json_str[json_str.find('{'):]
                            # Remove any text after the last }
                            json_str = json_str[:json_str.rfind('}')+1]
                            
                            # Fix common JSON issues
                            # Remove trailing commas before closing brackets
                            json_str = re.sub(r',\s*}', '}', json_str)
                            json_str = re.sub(r',\s*]', ']', json_str)
                            
                            # Fix missing commas between array elements
                            json_str = re.sub(r'}\s*{', '},{', json_str)
                            json_str = re.sub(r']\s*\[', '],[', json_str)
                            
                            # Fix missing commas between object properties
                            json_str = re.sub(r'"\s*"', '","', json_str)
                            json_str = re.sub(r'"\s*{', '",{', json_str)
                            json_str = re.sub(r'"\s*\[', '",[', json_str)
                            
                            # Remove any double commas
                            json_str = re.sub(r',\s*,', ',', json_str)
                            
                            # Ensure proper spacing
                            json_str = re.sub(r'\s+', ' ', json_str)
                            
                            # Log the cleaned JSON for debugging
                            logger.info(f"Cleaned JSON string: {json_str}")
                            
                            result = json.loads(json_str)
                            if result:
                                return result
                        except json.JSONDecodeError as e:
                            logger.error(f"Error parsing extracted JSON: {str(e)}")
                            logger.error(f"Problematic JSON string: {json_str}")
                    
                logger.warning(f"Attempt {attempt + 1}: Invalid JSON response")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
        return None

    def generate_workout_plan(self, user_level, recent_workouts, equipment, duration, workout_type, focus_area='full_body', intensity='medium'):
        try:
            # Format recent workouts for better context
            recent_workouts_str = "\n".join([
                f"- {w.exercise_name} ({w.workout_type}) on {w.date}"
                for w in recent_workouts
            ]) if recent_workouts else "No recent workouts"

            # Calculate number of exercises based on duration
            # 15-30 minutes: 3-4 exercises
            # 31-45 minutes: 4-5 exercises
            # 46-60 minutes: 5-6 exercises
            # 60+ minutes: 6-8 exercises
            if duration <= 30:
                num_exercises = "3-4"
            elif duration <= 45:
                num_exercises = "4-5"
            elif duration <= 60:
                num_exercises = "5-6"
            else:
                num_exercises = "6-8"

            # Create a more focused prompt for the AI
            prompt = f"""
            Create a {workout_type} workout plan for a {user_level} level user.
            Duration: {duration} minutes
            Focus Area: {focus_area}
            Intensity: {intensity}
            Equipment: {', '.join(equipment) if equipment else 'No equipment (bodyweight only)'}
            Recent workouts: {recent_workouts_str}
            Number of exercises: {num_exercises}

            Return ONLY a valid JSON object in this exact format:
            {{
                "title": "Workout title",
                "description": "Brief description",
                "exercises": [
                    {{
                        "name": "Exercise Name",
                        "sets": number_of_sets,
                        "reps": "reps_description",
                        "notes": "Brief form tip"
                    }}
                ],
                "tips": [
                    "Important tip 1",
                    "Important tip 2"
                ]
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
                "title": f"{workout_type.title()} {focus_area.replace('_', ' ').title()} Workout",
                "description": f"A {intensity} intensity {workout_type} workout focusing on {focus_area.replace('_', ' ')}.",
                "exercises": [
                    {
                        "name": "Push-ups",
                        "sets": 3,
                        "reps": "10-12",
                        "notes": "Keep your core tight"
                    },
                    {
                        "name": "Squats",
                        "sets": 3,
                        "reps": "12-15",
                        "notes": "Keep your back straight"
                    }
                ],
                "tips": [
                    "Focus on proper form",
                    "Stay hydrated"
                ]
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

    def generate_multi_day_workout_plan(self, user_level, recent_workouts, equipment, duration, workout_type, num_days):
        try:
            # Create a prompt for the AI
            prompt = f"""
            You are an expert fitness trainer creating a {num_days}-day workout plan. Consider the following information:
            - User Level: {user_level}
            - Recent Workouts: {recent_workouts}
            - Available Equipment: {equipment}
            - Preferred Duration: {duration} minutes per day
            - Preferred Workout Type: {workout_type}

            Create a {num_days}-day workout plan that:
            1. Is appropriate for the user's level
            2. Uses only the available equipment
            3. Fits within the specified duration per day
            4. Avoids exercises from recent workouts
            5. Includes proper warm-up and cool-down for each day
            6. Has clear progression instructions
            7. Ensures balanced training across different muscle groups
            8. Includes rest days where appropriate

            Return ONLY a valid JSON object in this exact format, with no additional text:
            {{
                "title": "Creative and engaging workout plan title",
                "description": "Detailed description of the workout plan and its benefits",
                "total_days": {num_days},
                "difficulty": "{user_level}",
                "days": [
                    {{
                        "day_number": day_number,
                        "title": "Day-specific title",
                        "description": "Day-specific description",
                        "duration": {duration},
                        "workout_type": "strength/cardio/flexibility/balance",
                        "exercises": [
                            {{
                                "name": "Exercise Name",
                                "sets": number_of_sets,
                                "reps": "reps_description",
                                "notes": "Form tips and modifications"
                            }}
                        ],
                        "notes": "Day-specific notes and instructions"
                    }}
                ],
                "progression": "Clear progression plan with specific goals"
            }}
            """

            logger.info(f"Generating {num_days}-day workout plan with prompt: {prompt}")
            
            # Generate response with retry logic
            workout_plan = self._generate_with_retry(prompt)
            
            if workout_plan:
                logger.info(f"Successfully generated {num_days}-day workout plan: {workout_plan}")
                return workout_plan
                
            # Return default workout plan if AI fails
            logger.warning("Using default workout plan due to AI generation failure")
            return {
                "title": f"{num_days}-Day Full Body Workout Plan",
                "description": f"A balanced {num_days}-day workout plan targeting all major muscle groups.",
                "total_days": num_days,
                "difficulty": user_level,
                "days": [
                    {
                        "day_number": i,
                        "title": f"Day {i} - Full Body Workout",
                        "description": "A balanced workout targeting all major muscle groups.",
                        "duration": int(duration) if duration else 45,
                        "workout_type": "strength",
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
                        "notes": "Focus on proper form and controlled movements"
                    } for i in range(1, num_days + 1)
                ],
                "progression": "Increase reps or duration by 10% each week"
            }
        except Exception as e:
            logger.error(f"Error generating multi-day workout plan: {str(e)}")
            raise

    def generate_7day_workout_plan(self, user_level, recent_workouts, equipment, duration, workout_type, focus_area='full_body', intensity='medium'):
        try:
            # Format recent workouts for better context
            recent_workouts_str = "\n".join([
                f"- {w.exercise_name} ({w.workout_type}) on {w.date}"
                for w in recent_workouts
            ]) if recent_workouts else "No recent workouts"

            # Calculate number of exercises based on duration
            if duration <= 30:
                num_exercises = "3-4"
            elif duration <= 45:
                num_exercises = "4-5"
            elif duration <= 60:
                num_exercises = "5-6"
            else:
                num_exercises = "6-8"

            # Create a prompt for the AI
            prompt = f"""
            Create a 7-day workout plan with these specific requirements:
            PRIMARY WORKOUT TYPE: {workout_type}
            DAILY DURATION: {duration} minutes
            FOCUS AREA: {focus_area}
            INTENSITY LEVEL: {intensity}
            EQUIPMENT: {', '.join(equipment) if equipment else 'No equipment (bodyweight only)'}

            The plan should:
            1. Focus primarily on {workout_type} exercises
            2. Target the {focus_area} area
            3. Maintain {intensity} intensity throughout
            4. Fit within {duration} minutes per day
            5. Include appropriate rest days
            6. Progress in difficulty throughout the week

            Return the plan in this exact format (one line per field):
            TITLE: 7-Day {workout_type.title()} {focus_area.replace('_', ' ').title()} Plan
            DESCRIPTION: Brief description focusing on {workout_type} and {focus_area}
            DAY1_TYPE: {workout_type}
            DAY1_TITLE: Day 1 - {workout_type.title()} {focus_area.replace('_', ' ').title()}
            DAY1_DESCRIPTION: Focus on {workout_type} exercises for {focus_area}
            DAY1_EXERCISE1_NAME: Exercise Name
            DAY1_EXERCISE1_SETS: number_of_sets
            DAY1_EXERCISE1_REPS: reps_description
            DAY1_EXERCISE1_NOTES: Brief form tip
            DAY1_TIP1: Important tip 1
            DAY1_TIP2: Important tip 2
            [Repeat for DAY2 through DAY7]
            WEEKLY_TIP1: Weekly tip 1
            WEEKLY_TIP2: Weekly tip 2
            """

            logger.info(f"Generating 7-day workout plan with prompt: {prompt}")
            
            # Generate response with retry logic
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            if response.text:
                # Parse the response into a structured format
                lines = response.text.strip().split('\n')
                plan_data = {}
                
                # Parse each line
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        plan_data[key.strip()] = value.strip()
                
                # Convert to JSON structure
                workout_plan = {
                    "title": plan_data.get('TITLE', f'7-Day {workout_type.title()} {focus_area.replace("_", " ").title()} Plan'),
                    "description": plan_data.get('DESCRIPTION', f'A {intensity} intensity {workout_type} plan focusing on {focus_area.replace("_", " ")}'),
                    "days": []
                }
                
                # Add each day
                for day in range(1, 8):
                    # Check if we have any data for this day
                    has_day_data = any(key.startswith(f'DAY{day}_') for key in plan_data.keys())
                    
                    if has_day_data:
                        day_data = {
                            "day": day,
                            "type": plan_data.get(f'DAY{day}_TYPE', workout_type),
                            "title": plan_data.get(f'DAY{day}_TITLE', f'Day {day} - {workout_type.title()} {focus_area.replace("_", " ").title()}'),
                            "description": plan_data.get(f'DAY{day}_DESCRIPTION', f'Day {day} {workout_type} workout focusing on {focus_area.replace("_", " ")}'),
                            "exercises": [],
                            "tips": []
                        }
                        
                        # Add exercises
                        exercise_num = 1
                        while f'DAY{day}_EXERCISE{exercise_num}_NAME' in plan_data:
                            try:
                                sets = int(plan_data.get(f'DAY{day}_EXERCISE{exercise_num}_SETS', '3'))
                            except (ValueError, TypeError):
                                sets = 3  # Default to 3 sets if value is invalid
                                
                            exercise = {
                                "name": plan_data[f'DAY{day}_EXERCISE{exercise_num}_NAME'],
                                "sets": sets,
                                "reps": plan_data.get(f'DAY{day}_EXERCISE{exercise_num}_REPS', '10-12'),
                                "notes": plan_data.get(f'DAY{day}_EXERCISE{exercise_num}_NOTES', '')
                            }
                            day_data["exercises"].append(exercise)
                            exercise_num += 1
                        
                        # Add tips
                        tip_num = 1
                        while f'DAY{day}_TIP{tip_num}' in plan_data:
                            day_data["tips"].append(plan_data[f'DAY{day}_TIP{tip_num}'])
                            tip_num += 1
                    else:
                        # Create a default day if no data is available
                        day_data = {
                            "day": day,
                            "type": workout_type,
                            "title": f"Day {day} - {workout_type.title()} {focus_area.replace('_', ' ').title()}",
                            "description": f"Day {day} {workout_type} workout focusing on {focus_area.replace('_', ' ')}",
                            "exercises": [
                                {
                                    "name": "Push-ups",
                                    "sets": 3,
                                    "reps": "10-12",
                                    "notes": "Keep your core tight"
                                },
                                {
                                    "name": "Squats",
                                    "sets": 3,
                                    "reps": "12-15",
                                    "notes": "Keep your back straight"
                                }
                            ],
                            "tips": [
                                "Focus on proper form",
                                "Stay hydrated"
                            ]
                        }
                    
                    workout_plan["days"].append(day_data)
                
                # Add weekly tips
                workout_plan["weekly_tips"] = []
                tip_num = 1
                while f'WEEKLY_TIP{tip_num}' in plan_data:
                    workout_plan["weekly_tips"].append(plan_data[f'WEEKLY_TIP{tip_num}'])
                    tip_num += 1
                
                logger.info(f"Successfully generated 7-day workout plan: {workout_plan}")
                return workout_plan
                
            # Return default workout plan if AI fails
            logger.warning("Using default 7-day workout plan due to AI generation failure")
            return {
                "title": f"7-Day {workout_type.title()} {focus_area.replace('_', ' ').title()} Plan",
                "description": f"A {intensity} intensity {workout_type} plan focusing on {focus_area.replace('_', ' ')}",
                "days": [
                    {
                        "day": i,
                        "type": workout_type,
                        "title": f"Day {i} - {workout_type.title()} {focus_area.replace('_', ' ').title()}",
                        "description": f"Day {i} {workout_type} workout focusing on {focus_area.replace('_', ' ')}",
                        "exercises": [
                            {
                                "name": "Push-ups",
                                "sets": 3,
                                "reps": "10-12",
                                "notes": "Keep your core tight"
                            },
                            {
                                "name": "Squats",
                                "sets": 3,
                                "reps": "12-15",
                                "notes": "Keep your back straight"
                            }
                        ],
                        "tips": [
                            "Focus on proper form",
                            "Stay hydrated"
                        ]
                    } for i in range(1, 8)
                ],
                "weekly_tips": [
                    "Rest when needed",
                    "Stay consistent with the plan"
                ]
            }
        except Exception as e:
            logger.error(f"Error generating 7-day workout plan: {str(e)}")
            raise 