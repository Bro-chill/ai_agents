import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize environment
load_dotenv()
api_key = os.getenv('GEMINI_KEY')
model = os.getenv('MODEL_CHOICE')

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=model,
    api_key=api_key,
    temperature=0.9,
)
