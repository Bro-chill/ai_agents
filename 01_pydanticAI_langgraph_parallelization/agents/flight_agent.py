from pydantic_ai import Agent, RunContext
from typing import Any, List, Dict
from dataclasses import dataclass
import logfire
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

logfire.configure(send_to_logfire='if-token-present')

model = get_model()

# Agent Dependencies
@dataclass
class FlightDeps:
    preferred_airlines: List[str]

# Agent prompt
system_prompt = """
You are  a flight specialist who helps users find the best flights for their trips.

Use the search_flights tool to find flight options and then provide personalized recommendation based on user's preferences.

The user's preferences are available in the context, including preferred airlines.

Always explain the reasoning behind your recommendations.

Format your response in a clear, organized way with flight details and prices.

Never ask for clarification on any piece of information before recommending flights,
just make your best guess for any parameters that you aren't sure of.
"""

flight_agent = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=FlightDeps,
    retries=4
)

@flight_agent.tool
async def search_flights(ctx: RunContext[FlightDeps], origin: str, destination: str, date: str) -> str:
    """Search for flights between two cities on a specific date, taking user preferences into account."""
    # In a real implementation, this would call a flight search API
    flight_options = [
        {
            "airline": "SkyWays",
            "departure_time": "08:00",
            "arrival_time": "10:30",
            "price": 350.00,
            "direct": True
        },
        {
            "airline": "OceanAir",
            "departure_time": "12:45",
            "arrival_time": "15:15",
            "price": 275.50,
            "direct": True
        },
        {
            "airline": "MountainJet",
            "departure_time": "16:30",
            "arrival_time": "21:45",
            "price": 225.75,
            "direct": False
        }
    ]
    
    # Apply user preferences if available
    if ctx.deps.preferred_airlines:
        preferred_airlines = ctx.deps.preferred_airlines
        if preferred_airlines:
            # Move preferred airlines to the top of the list
            flight_options.sort(key=lambda x: x["airline"] not in preferred_airlines)
            
            # Add a note about preference matching
            for flight in flight_options:
                if flight["airline"] in preferred_airlines:
                    flight["preferred"] = True                      
    
    return json.dumps(flight_options)    