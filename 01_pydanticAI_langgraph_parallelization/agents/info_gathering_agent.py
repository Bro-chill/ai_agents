from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Any, List, Dict
from dataclasses import dataclass
import logfire
import  json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

logfire.configure(send_to_logfire='if-token-present')

model = get_model()

# Agent output_type
class TravelDetails(BaseModel):
    """Details Type"""
    response: str = Field(description='Response to user if input is not complete')
    destination: str
    origin: str
    max_hotel_price: int
    date_leaving: str = Field(description='Format MM-DD')
    date_returning: str
    all_details_given: bool = Field(description='True or False details complete')

# Agent prompt
system_prompt = """
You are a travel planning assistant who helps users plan their trips.

Your goal is to gather all the necessary details from the user for their trip, including:
- Where they are going
- Where they are flying from
- Date they are leaving (month and day)
- Date they are returning (month and day)
- Max price for a hotel per night

Output all the information for the trip you have in the required format, and also ask user for missing information if necessary.
Tell the user what information is missing that they need to provide.
"""

info_gathering_agent = Agent(
    model,
    output_type=TravelDetails,
    system_prompt=system_prompt,
    retries=4
)