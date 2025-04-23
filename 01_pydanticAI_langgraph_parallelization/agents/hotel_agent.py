from pydantic_ai import Agent, RunContext
from typing import List, Dict, Optional
from dataclasses import dataclass
import logfire
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

logfire.configure(send_to_logfire='if-token-present')

model = get_model()

@dataclass
class HotelDeps:
    hotel_amenities: List[str]
    budget_level: str

system_prompt = """
You are a hotel specialist who helps users find the best accommodations for their trips.

Use the search_hotels tool to find hotel options, and then provide personalized recommendations
based on the user's preferences (location, amenities, price range).

The user's preferences are available in the context, including preferred amenities and budget level.

Always explain the reasoning behind your recommendations.

Format your response in a clear, organized way with hotel details, amenities, and prices.

Never ask for clarification on any piece of information before recommending hotels, just make
your best guess for any parameters that you aren't sure of.
"""

hotel_agent = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=HotelDeps,
    retries=4
)

@hotel_agent.tool
async def search_hotels(ctx: RunContext[HotelDeps], city: str, check_in: str, check_out: str, max_price: Optional[float] = None) -> str:
    """Search for hotels in a city for specific dates within a price range, taking user preferences into account."""
    # In a real implementation, this would call a hotel search API
    hotel_options = [
        {
            "name": "City Center Hotel",
            "location": "Downtown",
            "price_per_night": 199.99,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"]
        },
        {
            "name": "Riverside Inn",
            "location": "Riverside District",
            "price_per_night": 149.50,
            "amenities": ["WiFi", "Free Breakfast", "Parking"]
        },
        {
            "name": "Luxury Palace",
            "location": "Historic District",
            "price_per_night": 349.99,
            "amenities": ["WiFi", "Pool", "Spa", "Fine Dining", "Concierge"]
        }
    ]
    
    # Filter by max price if provided
    if max_price is not None:
        filtered_hotels = [hotel for hotel in hotel_options if hotel["price_per_night"] <= max_price]
    else:
        filtered_hotels = hotel_options
    
    # Apply user preferences if available
    preferred_amenities = ctx.deps.hotel_amenities
    budget_level = ctx.deps.budget_level
    
    # Sort hotels by preference match
    if preferred_amenities:
        # Calculate a score based on how many preferred amenities each hotel has
        for hotel in filtered_hotels:
            matching_amenities = [a for a in hotel["amenities"] if a in preferred_amenities]
            hotel["matching_amenities"] = matching_amenities
            hotel["preference_score"] = len(matching_amenities)
        
        # Sort by preference score (higher scores first)
        filtered_hotels.sort(key=lambda x: x["preference_score"], reverse=True)
    
    # Apply budget level preferences if available
    if budget_level:
        if budget_level == "budget":
            filtered_hotels.sort(key=lambda x: x["price_per_night"])
        elif budget_level == "luxury":
            filtered_hotels.sort(key=lambda x: x["price_per_night"], reverse=True)
        # mid-range is already handled by the max_price filter
        
    return json.dumps(filtered_hotels)