import os
import django
from google import genai

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitjacket.settings')
django.setup()

from django.conf import settings

def check_available_models():
    try:
        # Initialize with API key
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # List all available models
        models = client.list_models()
        
        print("Available models:")
        for model in models:
            print(f"- {model.name}")
            
    except Exception as e:
        print(f"Error checking models: {str(e)}")

if __name__ == "__main__":
    check_available_models() 