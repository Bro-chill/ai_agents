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
class LocationBreakdown(BaseModel):
    """Detailed location analysis"""
    locations_by_type: List[str] = Field(description='Locations categorized (interior/exterior, studio/practical)')
    location_requirements: List[str] = Field(description='Specific requirements for each location')
    set_construction_needs: List[str] = Field(description='Sets that need to be built')
    location_scouting_priorities: List[str] = Field(description='Priority locations for scouting')
    permit_requirements: List[str] = Field(description='Permit needs by location')
    accessibility_considerations: List[str] = Field(description='Crew and equipment access considerations')
    weather_dependencies: List[str] = Field(description='Weather-dependent scenes')
    location_budget_impact: List[str] = Field(description='Budget impact of each location')
    alternative_suggestions: List[str] = Field(description='Alternative location options')

# Prompt
system_prompt="""
    You are a location manager and production designer. Analyze the extracted script data for comprehensive location planning.

    ANALYZE:
    - All scene locations and their requirements
    - Interior vs exterior needs
    - Studio vs practical location needs
    - Set construction requirements
    - Permit and legal considerations
    - Accessibility for crew and equipment
    - Weather and timing dependencies
    - Budget implications of location choices
    - Alternative location options

    Provide actionable location breakdowns for production planning.
    """

# Agent
location_analysis_agent = Agent(
    model,
    output_type=LocationBreakdown,
    system_prompt=system_prompt
)

async def analyze_locations(raw_data: RawScriptData) -> LocationBreakdown:
    """Analyze locations based on extracted script data"""
    result = await location_analysis_agent.run(raw_data.model_dump_json())
    return result.output