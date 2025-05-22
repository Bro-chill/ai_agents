from agents2.research_agent import research_agent, AgentState, ResearchDeps
from agents2.summary_agent import summary_agent, SummaryDeps

from langgraph.graph import StateGraph,START,END
from typing import Annotated, Dict, List, Any, Literal
from typing_extensions import TypedDict
from dataclasses import dataclass

# Define state for graph(Same as AgentState)

# Define the router function
def router(state: AgentState) -> Literal["research_agent", "summary_agent", "END"]:
    """Determine which agent should run next based on the current state."""
    # If the summary agent has completed its task, we're done
    if state.task_complete and state.current_agent == "summary_agent":
        return "END"
    
    # If research is done, move to summary
    if state.current_agent == "research_agent" and state.research_results:
        return "summary_agent"
    
    # Default to research agent
    return "research_agent"

# Define node for each agent

# research_agent node
async def run_research_agent(state: AgentState):
    # Access attributes directly, not with dictionary notation
    messages_details = state.messages
    research_dep = ResearchDeps()

    prompt = f"Running research agent with input: {messages_details}"
    result = await research_agent.run(prompt, deps=research_dep)
    
    # The result is already an AgentState object, so we can use it directly
    # But we need to preserve the original messages
    result_state = result.output
    
    # Create a new state with updated values
    new_state = state.model_copy(update={
        "current_agent": "research_agent",
        "research_results": result_state.research_results or f"Detailed research about {messages_details}",
        "summary": None
    })
    
    return new_state

# summary_agent node
async def run_summary_agent(state: AgentState):
    # Access attributes directly
    research_details = state.research_results
    summary_dep = SummaryDeps()

    prompt = f"Please summarize the following research results: {research_details}"
    result = await summary_agent.run(prompt, deps=summary_dep)
    
    # The result is already an AgentState object
    result_state = result.output
    
    # Create a new state with updated values
    new_state = state.model_copy(update={
        "current_agent": "summary_agent",
        "summary": result_state.summary or f"Summary of research on {state.messages}",
        "task_complete": True
        # Don't modify research_results here to preserve it
    })
    
    return new_state

# Define graph
def create_workflow():
    """Create and return the agent workflow."""
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph with wrapper functions
    workflow.add_node("research_agent", run_research_agent)
    workflow.add_node("summary_agent", run_summary_agent)

    workflow.add_edge(START,"research_agent")
    workflow.add_edge("research_agent","summary_agent")
    workflow.add_edge("summary_agent",END)
    
    # Compile the graph
    return workflow.compile()

# Function to run
async def run_workflow(query: str):
    """Run the workflow with the given query."""
    # Create the app
    app = create_workflow()
    
    # Initialize state with user query - COMPLETELY FRESH STATE
    initial_state = AgentState(
        messages=query,  # Store the query directly
        current_agent=None,
        research_results=None,
        summary=None,
        task_complete=False,
        next_agent=None
    )
    
    print(f"Initial state: {initial_state}")
    
    # Execute the workflow
    result = await app.ainvoke(initial_state)
    
    return result

async def main():
    """Main function to demonstrate the workflow."""
    query = "Tell me about quantum computing"
    final_state = await run_workflow(query)
    
    # Print the results
    print("\n=== CONVERSATION ===")
    for message in final_state.messages:
        print(f"\n{message}\n")
    
    print("\n=== RESEARCH RESULTS ===")
    print(final_state.research_results)
    
    print("\n=== SUMMARY ===")
    print(final_state.summary)

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())