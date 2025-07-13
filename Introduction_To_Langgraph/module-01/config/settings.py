import os
from dotenv import load_dotenv

# Initialize environment
load_dotenv()

# Environment variables
GEMINI_KEY = os.getenv("GEMINI_KEY")
MODEL_CHOICE = os.getenv("MODEL_CHOICE")
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

# Agent configuration
AGENT_CONFIG = {
    "temperature": 0.0,
    "verbose": True,
    "max_iterations": 5
}