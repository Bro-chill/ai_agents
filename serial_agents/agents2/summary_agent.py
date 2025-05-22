from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Any, Annotated, List, Dict, Optional
from dataclasses import dataclass

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

model = get_model()

# Declare state for globa agent
class AgentState(BaseModel):
    """Shared state between agents."""
    messages: str
    current_agent: Optional[str] = None
    task_complete: bool = False
    research_results: Optional[str] = None
    summary: Optional[str] = None
    next_agent: Optional[str] = None

# Declare dependencies for summary agent
class SummaryDeps(BaseModel):
    """Dependencies for the summary agent."""
    max_length: int = 150

# Declare prompt for agent
system_prompt = """
You are a summarization assistant that creates concise summaries of research findings.
"""

summary_agent = Agent(
    model=model,
    deps_type=SummaryDeps,
    output_type=AgentState,
    system_prompt=system_prompt,
    output_retries=2
)