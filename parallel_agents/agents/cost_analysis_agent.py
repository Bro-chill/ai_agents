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
class CostBreakdown(BaseModel):
    """Detailed cost analysis"""
    estimated_budget_range: str = Field(description='Budget range (low/medium/high/premium)')
    estimated_shoot_days: int = Field(description='Estimated shooting days needed')
    crew_size_recommendation: str = Field(description='Recommended crew size')
    location_costs: List[str] = Field(description='Cost assessment per location')
    equipment_costs: List[str] = Field(description='Major equipment cost factors')
    talent_requirements: List[str] = Field(description='Talent cost considerations')
    post_production_complexity: str = Field(description='Post-production cost level')
    total_cost_drivers: List[str] = Field(description='Main factors driving costs')
    cost_optimization_suggestions: List[str] = Field(description='Ways to reduce costs')

# Prompt
system_prompt="""
    You are a film production cost analysis expert. Analyze the extracted script data to provide detailed cost estimates.

    ANALYZE:
    - Location complexity and rental costs
    - Equipment needs and rental costs  
    - Crew size requirements
    - Talent/casting costs
    - Props and costume budgets
    - Post-production requirements
    - Shooting schedule impact on costs

    Provide realistic cost assessments based on industry standards.
    """

# Agent
cost_analysis_agent = Agent(
    model,
    output_type=CostBreakdown,
    system_prompt=system_prompt
)

async def analyze_costs(raw_data: RawScriptData) -> CostBreakdown:
    """Analyze costs based on extracted script data"""
    return await cost_analysis_agent.run(raw_data.model_dump_json())