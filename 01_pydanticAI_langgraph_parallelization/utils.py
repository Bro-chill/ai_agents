from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from dotenv import load_dotenv
import os

load_dotenv()

def get_model():
    llm = os.getenv('MODEL_CHOICE', 'gemma3:4b')
    base_url = os.getenv('BASE_URL', 'http://localhost:11434')

    return OpenAIModel(
        model_name=llm,
        provider=OpenAIProvider(base_url=base_url),
    )