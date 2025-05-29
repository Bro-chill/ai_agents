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
class SceneBreakdown(BaseModel):
    """Detailed scene analysis"""
    scene_structure: List[str] = Field(description='Scene-by-scene breakdown with details')
    pacing_analysis: str = Field(description='Overall pacing and rhythm analysis')
    dramatic_structure: List[str] = Field(description='Three-act structure breakdown')
    key_scenes: List[str] = Field(description='Critical scenes for the story')
    action_vs_dialogue_ratio: List[str] = Field(description='Action to dialogue ratio by scene')
    emotional_beats: List[str] = Field(description='Emotional progression through scenes')
    scene_complexity: List[str] = Field(description='Production complexity by scene')
    continuity_requirements: List[str] = Field(description='Continuity considerations between scenes')

# Prompt
system_prompt="""
    You are a script supervisor and story analyst. Analyze the extracted script data for comprehensive scene breakdowns.

    ANALYZE:
    - Scene structure and organization
    - Dramatic pacing and rhythm
    - Story beats and emotional progression
    - Action vs dialogue balance
    - Scene complexity for production
    - Continuity requirements
    - Key dramatic moments
    - Overall narrative structure

    Provide detailed scene analysis for production planning and direction.
    """

# Agent
scene_breakdown_agent = Agent(
    model,
    output_type=SceneBreakdown,
    system_prompt=system_prompt
)

async def analyze_scenes(raw_data: RawScriptData) -> SceneBreakdown:
    """Analyze scene structure based on extracted script data"""
    result = await scene_breakdown_agent.run(raw_data.model_dump_json())
    return result.output