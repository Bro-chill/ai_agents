from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from dotenv import load_dotenv
import os

load_dotenv()

def get_model():
    model_name = os.getenv('MODEL_CHOICE')
    api_key = os.getenv('GEMINI_KEY')
    
    # Initialize the provider with the API key
    provider = GoogleGLAProvider(api_key=api_key)
    
    # Create GeminiModel with the provider
    return GeminiModel(model_name, provider=provider)