import google.generativeai as genai
import json

def test_gemini_api():
    try:
        # Initialize Gemini with API key
        api_key = 'AIzaSyBptxfb1gNKbXKfrNAhez8gyMX_OttrwGk'
        print("Using API key:", api_key)
        
        genai.configure(api_key=api_key)
        print("Configured Gemini API")
        
        model = genai.GenerativeModel('gemini-pro')
        print("Created model instance")
        
        # Simple test prompt
        prompt = """
        Generate a simple workout plan in JSON format:
        {
            "title": "Test Workout",
            "exercises": [
                {
                    "name": "Exercise Name",
                    "sets": 3,
                    "reps": "10"
                }
            ]
        }
        """
        print("Sending prompt:", prompt)
        
        # Generate response
        response = model.generate_content(prompt)
        print("API Response:", response.text)
        
        # Try to parse as JSON
        workout = json.loads(response.text)
        print("Parsed JSON:", workout)
        
        return True
    except Exception as e:
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    print("Starting API test...")
    result = test_gemini_api()
    print("Test completed. Success:", result) 