from langgraph.graph import StateGraph, MessagesState, START, END
from config import Configuration
from nodes import (
    task_mAIstro, 
    update_todos, 
    update_profile, 
    update_instructions, 
    route_message
)

def create_graph():
    """Create and return the compiled graph."""
    builder = StateGraph(MessagesState, config_schema=Configuration)

    # Define nodes
    builder.add_node("task_mAIstro", task_mAIstro)
    builder.add_node("update_todos", update_todos)
    builder.add_node("update_profile", update_profile)
    builder.add_node("update_instructions", update_instructions)

    # Define the flow 
    builder.add_edge(START, "task_mAIstro")
    builder.add_conditional_edges(
        "task_mAIstro", 
        route_message,
        {
            "update_todos": "update_todos",
            "update_profile": "update_profile", 
            "update_instructions": "update_instructions",
            "__end__": END
        }
    )
    builder.add_edge("update_todos", "task_mAIstro")
    builder.add_edge("update_profile", "task_mAIstro")
    builder.add_edge("update_instructions", "task_mAIstro")

    return builder