from pydantic_ai import Agent
import logfire
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_model

logfire.configure(send_to_logfire='if-token-present')

model = get_model()

system_prompt = """
You are a travel agent expert helping people plan their perfect trip.

You will be given flight, hotel, and activity recommendations, and it's your job to take all
of that information and summarize it in a neat final package to give to the user as your
final recommendation for their trip.
"""

final_planner_agent = Agent(model, system_prompt=system_prompt)