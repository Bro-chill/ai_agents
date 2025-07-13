import uuid
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from graph import create_graph
from utils import display_todo_list

def interactive_chat(user_id: str = "default-user"):
    """
    Interactive chat function that maintains conversation history.
    """
    # Create persistent components
    memory = MemorySaver()
    store = InMemoryStore()
    builder = create_graph()
    app = builder.compile(checkpointer=memory, store=store)
    
    # Generate unique thread for this conversation
    thread_id = str(uuid.uuid4())
    
    config = {
        "configurable": {
            "user_id": user_id,
            "thread_id": thread_id
        }
    }
    
    print("Chatbot: Hello! I'm your personal assistant. I can help you manage your tasks and remember important information.")
    print("Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Chatbot: Goodbye!")
            break
        
        try:
            result = app.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            response = result["messages"][-1].content
            print(f"Chatbot: {response}")
            
            # Display the current ToDo list after each response
            todo_display = display_todo_list(store, user_id)
            print(f"\n{todo_display}\n")
            
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    interactive_chat("user_123")