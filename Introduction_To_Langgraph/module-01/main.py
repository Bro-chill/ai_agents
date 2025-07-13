from agents import create_agent_executor

def chatbot(agent_executor):
    """Main CLI chat function"""
    print("🤖 AI Assistant with Tools")
    print("Type 'quit', 'exit', or 'bye' to end the conversation")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n🤖 Assistant: Goodbye! Have a great day!")
                break
            
            # Skip empty inputs
            if not user_input:
                continue
            
            # Process the input through the agent
            print("\n🤖 Assistant: ", end="")
            response = agent_executor.invoke({"input": user_input})
            print(response["output"])
            
        except KeyboardInterrupt:
            print("\n\n🤖 Assistant: Goodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    # Create the agent executor
    agent_executor = create_agent_executor()
    
    # Start the chatbot
    chatbot(agent_executor)