from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional
from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

model = get_model()

# Shared state between agents
class AgentState(BaseModel):
    """Shared state between agents."""
    messages: str
    current_agent: Optional[str] = None
    task_complete: bool = False
    research_results: Optional[str] = None
    summary: Optional[str] = None

@dataclass
class ResearchDeps:
    """Dependencies for the research agent."""
    topic: str = "general topic"
    depth: int = 3

system_prompt = """
You are a research assistant that provides in-depth information on various topics.
Research the given topic thoroughly and provide comprehensive information.

IMPORTANT: You must return a valid AgentState object with:
- messages: keep the original query
- current_agent: set to "research_agent"
- research_results: your detailed research findings (required)
- task_complete: set to False
- summary: leave as None

Always provide detailed research_results content.
"""

research_agent = Agent(
    model=model,
    deps_type=ResearchDeps,
    output_type=AgentState,  # Changed from output_type
    system_prompt=system_prompt,
    retries=2
)

@research_agent.tool_plain
async def search_information(query: str) -> str:
    """Search for information on the given query."""
    return f"Mock search results for: {query}"