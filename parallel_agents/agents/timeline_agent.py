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
class TimelineBreakdown(BaseModel):
    """Detailed timeline and scheduling analysis"""
    shooting_schedule_estimate: List[str] = Field(description='Estimated days needed by location/setup')
    scene_grouping_recommendations: List[str] = Field(description='Scenes that should be shot together')
    location_shooting_order: List[str] = Field(description='Recommended order for location shooting')
    cast_availability_requirements: List[str] = Field(description='When each actor is needed')
    equipment_scheduling: List[str] = Field(description='Equipment needs by shooting period')
    pre_production_timeline: List[str] = Field(description='Pre-production milestones and timing')
    post_production_timeline: List[str] = Field(description='Post-production phases and timing')
    critical_path_items: List[str] = Field(description='Items that could delay production')
    buffer_recommendations: List[str] = Field(description='Recommended time buffers')

# Prompt
system_prompt="""
    You are a production scheduler and first assistant director. Analyze the extracted script data for comprehensive timeline and scheduling planning.

    ANALYZE:
    - Shooting schedule requirements
    - Scene grouping for efficiency
    - Location shooting order optimization
    - Cast scheduling requirements
    - Equipment and crew scheduling
    - Pre-production timeline needs
    - Post-production scheduling
    - Critical path dependencies
    - Risk factors and buffer needs

    Provide detailed timeline analysis for production scheduling.
    """

# Agent
timeline_agent = Agent(
    model,
    output_type=TimelineBreakdown,
    system_prompt=system_prompt
)

async def analyze_timeline(raw_data: RawScriptData) -> TimelineBreakdown:
    """Analyze timeline and scheduling based on extracted script data"""
    result = await timeline_agent.run(raw_data.model_dump_json())
    return result.output