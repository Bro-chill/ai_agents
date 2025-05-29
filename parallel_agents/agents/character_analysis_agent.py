from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model
from .info_gathering_agent import RawScriptData

model = get_model()

# State/Output type
class CharacterBreakdown(BaseModel):
    """Detailed character analysis"""
    main_characters: List[str] = Field(description='Main characters with role, age, description')
    supporting_characters: List[str] = Field(description='Supporting characters details')
    background_characters: List[str] = Field(description='Background/extra characters')
    character_relationships: List[str] = Field(description='Character relationship mapping')
    dialogue_analysis: List[str] = Field(description='Dialogue style and complexity by character')
    casting_requirements: List[str] = Field(description='Casting specifications for each character')
    character_arcs: List[str] = Field(description='Character development arcs')
    ensemble_dynamics: str = Field(description='Overall cast dynamics and chemistry requirements')

# Prompt
system_prompt = """
    You are a casting director and character development specialist. Analyze the extracted script data for comprehensive character breakdowns.

    ANALYZE:
    - Character hierarchy (main, supporting, background)
    - Character relationships and dynamics
    - Dialogue patterns and complexity
    - Casting requirements and specifications
    - Character development arcs
    - Age, gender, and physical requirements
    - Special skills or abilities needed
    - Ensemble chemistry requirements

    Provide detailed character analysis for casting and direction.
    """

# Agent
character_analysis_agent = Agent(
    model,
    output_type=CharacterBreakdown,
    system_prompt=system_prompt
)

async def analyze_characters(raw_data: RawScriptData) -> CharacterBreakdown:
    """Analyze characters based on extracted script data"""
    result = await character_analysis_agent.run(raw_data.model_dump_json())
    return result.output