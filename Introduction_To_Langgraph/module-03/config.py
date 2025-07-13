import os
from dataclasses import dataclass, fields
from typing import Optional, Any
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    user_id: str = "default-user"

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})

# Initialize the LLM
def get_llm():
    api_key = os.getenv('GEMINI_KEY')
    model = os.getenv('MODEL_CHOICE')
    
    return ChatGoogleGenerativeAI(
        model=model,
        api_key=api_key,
        temperature=0.9,
    )