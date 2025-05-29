from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model
from .info_gathering_agent import RawScriptData

model = get_model()

# State/Ouput type
class PropsBreakdown(BaseModel):
    """Detailed props analysis"""
    props_by_category: List[str] = Field(description='Props organized by category (weapons, furniture, electronics, etc.)')
    costume_requirements: List[str] = Field(description='Costumes by character')
    makeup_requirements: List[str] = Field(description='Makeup and prosthetics needed')
    set_decoration: List[str] = Field(description='Set decoration and dressing items')
    special_props: List[str] = Field(description='Custom or special effect props')
    prop_complexity: List[str] = Field(description='Complexity level for each major prop')
    sourcing_recommendations: List[str] = Field(description='Where to source each prop type')
    prop_budget_estimate: str = Field(description='Overall props budget category')

# Prompt
system_prompt="""
    You are a props master and costume designer. Analyze the extracted script data to create comprehensive props and costume breakdowns.

    ANALYZE:
    - All physical items mentioned in script
    - Character costume requirements
    - Makeup and prosthetics needs
    - Set decoration requirements
    - Special or custom props needed
    - Categorize by complexity and sourcing difficulty
    - Estimate budget requirements

    Provide detailed, actionable props lists for production teams.
    """

# Agent
props_extraction_agent = Agent(
    model,
    output_type=PropsBreakdown,
    system_prompt=system_prompt
)

async def analyze_props(raw_data: RawScriptData) -> PropsBreakdown:
    """Analyze props and costumes based on extracted script data"""
    result = await props_extraction_agent.run(raw_data.model_dump_json())
    return result.output