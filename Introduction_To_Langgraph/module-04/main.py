from graphs.research_graph import build_research_graph

# Build and compile the graph
graph = build_research_graph()

# Example usage
if __name__ == "__main__":
    # Example state
    initial_state = {
        "topic": "Artificial Intelligence in Healthcare",
        "max_analysts": 3,
        "human_analyst_feedback": "approve"
    }
    
    # Run the graph
    result = graph.invoke(initial_state)
    print(result["final_report"])