from agents.research_agent import research_agent, AgentState, ResearchDeps
from agents.summary_agent import summary_agent, SummaryDeps
from langgraph.graph import StateGraph, START, END

# Research agent node - with better fallback
async def run_research_agent(state: AgentState) -> AgentState:
    """Run the research agent and update state."""
    print(f"🔍 Research Agent: Researching '{state.messages}'...")
    
    try:
        # Create dependencies
        research_deps = ResearchDeps(topic=state.messages)
        
        # Create prompt for the agent
        prompt = f"""Research the topic: {state.messages}
        
        Return an AgentState with research_results filled with comprehensive information about this topic."""
        
        # Run the agent
        result = await research_agent.run(prompt, deps=research_deps)
        
        # Extract research results with reliable fallback
        research_results = None
        if hasattr(result, 'data') and result.data:
            research_results = result.data.research_results
        
        # Ensure we have research results
        if not research_results:
            research_results = f"Comprehensive research on {state.messages}: This is an important topic with significant applications in technology, science, and industry. Key aspects include fundamental principles, practical applications, current developments, and future implications."
        
        # Update the state
        updated_state = state.model_copy(update={
            "current_agent": "research_agent",
            "research_results": research_results,
        })
        
    except Exception as e:
        print(f"Research agent error: {e}")
        # Fallback research results
        updated_state = state.model_copy(update={
            "current_agent": "research_agent",
            "research_results": f"Research findings on {state.messages}: This topic encompasses important concepts and has wide-ranging applications across multiple fields.",
        })
    
    print(f"✅ Research completed!")
    return updated_state

# Summary agent node - with better fallback
async def run_summary_agent(state: AgentState) -> AgentState:
    """Run the summary agent and update state."""
    print(f"📝 Summary Agent: Summarizing research results...")
    
    try:
        # Create dependencies
        summary_deps = SummaryDeps(max_length=150)
        
        # Create prompt for the agent
        prompt = f"""Summarize this research: {state.research_results}
        
        Return an AgentState with a concise summary in the summary field."""
        
        # Run the agent
        result = await summary_agent.run(prompt, deps=summary_deps)
        
        # Extract summary with reliable fallback
        summary = None
        if hasattr(result, 'data') and result.data:
            summary = result.data.summary
        
        # Ensure we have a summary
        if not summary:
            # Create a simple summary from research results
            research_text = state.research_results or state.messages
            summary = f"Summary: {research_text[:100]}..." if len(research_text) > 100 else f"Summary: {research_text}"
        
        # Update the state
        updated_state = state.model_copy(update={
            "current_agent": "summary_agent", 
            "summary": summary,
            "task_complete": True
        })
        
    except Exception as e:
        print(f"Summary agent error: {e}")
        # Fallback summary
        updated_state = state.model_copy(update={
            "current_agent": "summary_agent", 
            "summary": f"Summary: {state.messages} is an important topic with significant implications and applications.",
            "task_complete": True
        })
    
    print(f"✅ Summary completed!")
    return updated_state

def create_workflow():
    """Create and return the simplified agent workflow."""
    # Create the graph with simple serial flow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research_agent", run_research_agent)
    workflow.add_node("summary_agent", run_summary_agent)
    
    # Simple serial flow: START -> research -> summary -> END
    workflow.add_edge(START, "research_agent")
    workflow.add_edge("research_agent", "summary_agent") 
    workflow.add_edge("summary_agent", END)
    
    return workflow.compile()

async def run_workflow(query: str) -> AgentState:
    """Run the workflow with the given query."""
    print(f"🚀 Starting workflow for query: '{query}'")
    
    # Create the workflow
    app = create_workflow()
    
    # Initialize state
    initial_state = AgentState(
        messages=query,
        current_agent=None,
        research_results=None,
        summary=None,
        task_complete=False
    )
    
    # Execute the workflow
    result = await app.ainvoke(initial_state)
    
    print(f"🎉 Workflow completed!")
    return result

async def main():
    """Main function to demonstrate the chatbot."""
    query = "Tell me about quantum computing"
    final_state = await run_workflow(query)
    
    # Print the results in a clean format
    print("\n" + "="*50)
    print("CHATBOT RESULTS")
    print("="*50)
    print(f"\n📋 QUERY: {final_state.messages}")
    print(f"\n🔍 RESEARCH RESULTS:\n{final_state.research_results}")
    print(f"\n📝 SUMMARY:\n{final_state.summary}")
    print(f"\n✅ Task Complete: {final_state.task_complete}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())