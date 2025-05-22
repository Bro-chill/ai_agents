from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Any, Annotated, List, Dict, Optional
from dataclasses import dataclass

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

model = get_model()

# Declare state for global agent
class AgentState(BaseModel):
    """Shared state between agents."""
    messages: str
    current_agent: Optional[str] = None
    task_complete: bool = False
    research_results: Optional[str] = None
    summary: Optional[str] = None
    next_agent: Optional[str] = None

# Declare dependencies for research agent
@dataclass
class ResearchDeps:
    """Dependencies for the research agent."""
    topic: str = "general topic"
    depth: int = 3

# Declare prompt for agent
system_prompt = """
You are a research assistant that provides in-depth information on various topics.
Your goal is to research the given topic thoroughly and provide comprehensive information.
"""

research_agent = Agent(
    model=model,
    deps_type=ResearchDeps,
    output_type=AgentState,
    system_prompt=system_prompt,
    output_retries=2
)

# Declare tool for agent
@research_agent.tool_plain
async def search_information(messages: str) -> str:
    """Search for information on the given messages."""
    return f"Mock search results for: {messages}"
