from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

model = get_model()

# Same shared state
class AgentState(BaseModel):
    """Shared state between agents."""
    messages: str
    current_agent: Optional[str] = None
    task_complete: bool = False
    research_results: Optional[str] = None
    summary: Optional[str] = None

class SummaryDeps(BaseModel):
    """Dependencies for the summary agent."""
    max_length: int = 150

system_prompt = """
You are a summarization assistant that creates concise summaries of research findings.
Take the research results and create a clear, concise summary.

IMPORTANT: You must return a valid AgentState object with:
- messages: keep the original query
- current_agent: set to "summary_agent"
- research_results: keep the existing research results
- summary: your concise summary (required)
- task_complete: set to True

Always provide a clear summary in the summary field.
"""

summary_agent = Agent(
    model=model,
    deps_type=SummaryDeps,
    output_type=AgentState,  # Changed from output_type
    system_prompt=system_prompt,
    retries=2
)