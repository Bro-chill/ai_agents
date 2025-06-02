from typing import Annotated

from typing_extensions import TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import interrupt

# Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    needs_human_review: bool = False

graph_builder = StateGraph(State)

# Create nodes
def chatbot(state: State):
    message = llm.invoke(state["messages"])
    
    # Determine if human review is needed (customize this logic)
    needs_review = (
        len(message.content) > 500 or  # Long responses
        "sensitive" in message.content.lower() or  # Sensitive content
        state.get("needs_human_review", False)  # Explicitly requested
    )
    
    return {
        "messages": [message],
        "needs_human_review": needs_review
    }

def human_review(state: State):
    """Human review node"""
    last_message = state["messages"][-1]
    
    human_input = interrupt({
        "message": "Review required for AI response:",
        "ai_response": last_message.content,
        "action_needed": "approve, modify, or reject"
    })
    
    if human_input.get("action") == "modify":
        from langchain_core.messages import AIMessage
        modified_content = human_input.get("modified_response", last_message.content)
        messages = state["messages"][:-1]
        return {
            "messages": [AIMessage(content=modified_content)],
            "needs_human_review": False
        }
    
    return {"needs_human_review": False}

def should_review(state: State) -> str:
    """Conditional function to determine if human review is needed"""
    if state.get("needs_human_review", False):
        return "human_review"
    return END

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("human_review", human_review)

# Build graph
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    should_review,
    {
        "human_review": "human_review",
        END: END
    }
)
graph_builder.add_edge("human_review", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory, interrupt_before=["human_review"])

# Function to explore state history
def explore_state_history(config, target_message_count=6):
    """
    Explore the state history and optionally find a specific state to replay
    
    Args:
        config: Configuration with thread_id
        target_message_count: Number of messages to look for when selecting a state to replay
    
    Returns:
        State object if found, None otherwise
    """
    to_replay = None
    
    print("=== STATE HISTORY ===")
    for i, state in enumerate(graph.get_state_history(config)):
        print(f"State {i}:")
        print(f"  Num Messages: {len(state.values['messages'])}")
        print(f"  Next: {state.next}")
        print(f"  Needs Review: {state.values.get('needs_human_review', False)}")
        
        # Print last message content if exists
        if state.values["messages"]:
            last_msg = state.values["messages"][-1]
            content_preview = last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content
            print(f"  Last Message: {content_preview}")
        
        print("-" * 80)
        
        # Select state based on message count
        if len(state.values["messages"]) == target_message_count:
            to_replay = state
            print(f"*** SELECTED STATE {i} FOR REPLAY ***")
            print("-" * 80)
    
    return to_replay

# Usage example function
def replay_from_state(to_replay_state, config):
    """
    Replay the graph from a specific state
    
    Args:
        to_replay_state: State object to replay from
        config: Configuration with thread_id
    """
    if to_replay_state:
        print("=== REPLAYING FROM SELECTED STATE ===")
        print(f"Replaying from state with {len(to_replay_state.values['messages'])} messages")
        
        # Update the graph to the selected state
        graph.update_state(config, to_replay_state.values)
        
        # Continue execution from that point
        result = graph.invoke(None, config)
        return result
    else:
        print("No state selected for replay")
        return None

# Example usage:
# config = {"configurable": {"thread_id": "conversation-1"}}
# 
# # After running some conversations...
# to_replay = explore_state_history(config, target_message_count=6)
# 
# # Replay from the selected state
# if to_replay:
#     result = replay_from_state(to_replay, config)