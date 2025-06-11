from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional
from dataclasses import dataclass
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

model = get_model()

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
You are a research assistant that provides comprehensive information on various topics.

Your task is to research the given topic and provide detailed, factual information using your knowledge base. 

For any topic, provide:
1. Overview and key facts
2. Historical context
3. Current significance
4. Important characteristics
5. Relevant applications or implications

IMPORTANT INSTRUCTIONS:
- Use your built-in knowledge to provide comprehensive information
- Do NOT reference "mock search results" or external tools
- Provide at least 150-200 words of substantive content
- Focus on factual, educational information

You must return a valid AgentState object with:
- messages: keep the original query exactly as received
- current_agent: set to "research_agent"
- research_results: your detailed research findings (comprehensive and factual)
- task_complete: set to False
- summary: leave as None

Always provide substantial, informative content about the requested topic.
"""

research_agent = Agent(
    model=model,
    deps_type=ResearchDeps,
    result_type=AgentState,
    system_prompt=system_prompt,
    retries=2
)
