import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, RemoveMessage

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END

load_dotenv()
api_key = os.getenv('GEMINI_KEY')
model = os.getenv('MODEL_CHOICE')

llm = ChatGoogleGenerativeAI(
    model=model,
    api_key=api_key,
    temperature=0,
)

# State for summary
class SummaryState(MessagesState):
    summary: str

# Call model function
def call_model(state: SummaryState):
    summary = state.get("summary", "")

    if summary:
        system_message = f"Summary of conversation earlier: {summary}"
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]
    
    response = llm.invoke(messages)
    return {"messages": [response]}  # Return as list

# Summarizer function
def summarize_conversation(state: SummaryState):
    summary = state.get("summary", "")

    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = llm.invoke(messages)

    # Delete all except 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]  # Fixed typo
    return {"summary": response.content, "messages": delete_messages}

# Conditional edge function
def should_continue(state: SummaryState):
    """Return the next node to execute"""
    messages = state["messages"]
    
    if len(messages) > 6:
        return "summarize_conversation"
    
    return END

# Define graph
workflow = StateGraph(SummaryState)

workflow.add_node("conversation", call_model)
workflow.add_node("summarize_conversation", summarize_conversation)

workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

def run_conversation():
    config = {"configurable": {"thread_id": "conversation_1"}}  # Added thread config
    
    # Initialize with a greeting
    initial_state = {"messages": [AIMessage("Hi! How can I help you today?", name="Bot")]}
    graph.invoke(initial_state, config)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        
        # Add user message and invoke graph
        user_message = HumanMessage(content=user_input, name="User")
        result = graph.invoke({"messages": [user_message]}, config)
        
        # Get the latest bot response
        if result["messages"]:
            bot_response = result["messages"][-1]
            print(f"Bot: {bot_response.content}")
        
        # Optional: Print current summary if it exists
        if "summary" in result and result["summary"]:
            print(f"[Summary: {result['summary']}]")

if __name__ == "__main__":
    run_conversation()