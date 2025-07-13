from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config.settings import GEMINI_KEY, MODEL_CHOICE, AGENT_CONFIG
from tools import (
    calculator,
    wikipedia_search,
    research_paper_search,
    tavily_search,
    currency_exchange
)

def create_agent_executor():
    """Create and return the agent executor with all tools configured"""
    
    # Initialize LLM
    llm = ChatGoogleGenerativeAI(
        model=MODEL_CHOICE,
        api_key=GEMINI_KEY,
        temperature=AGENT_CONFIG["temperature"],
    )
    
    # Define tools
    tools = [
        calculator,
        wikipedia_search,
        research_paper_search,
        tavily_search,
        currency_exchange
    ]
    
    # Define prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant with access to various tools. Use the tools when needed to provide accurate and helpful responses."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=AGENT_CONFIG["verbose"],
        max_iterations=AGENT_CONFIG["max_iterations"]
    )
    
    return agent_executor