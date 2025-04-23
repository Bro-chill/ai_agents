from langgraph.types import Command
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import streamlit as st
import asyncio
import uuid
import json
import os

from agent_graph import travel_agent_graph


# Page configuration
st.set_page_config(
    page_title="Travel Planner Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - minimal now that we're using Streamlit's chat components
st.markdown("""
<style>
    .stChatMessage {
        margin-bottom: 1rem;
    }
    .stChatMessage .content {
        padding: 0.5rem;
    }
    .stChatMessage .timestamp {
        font-size: 0.8rem;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

class UserContext(BaseModel):
    user_id: str
    preferred_airlines: List[str]
    hotel_amenities: List[str]
    budget_level: str

@st.cache_resource
def get_thread_id():
    return str(uuid.uuid4())

thread_id = get_thread_id()

# Initialize session state for chat history and user context
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "user_context" not in st.session_state:
    st.session_state.user_context = UserContext(
        user_id=str(uuid.uuid4()),
        preferred_airlines=[],
        hotel_amenities=[],
        budget_level="mid-range"
    )

if "processing_message" not in st.session_state:
    st.session_state.processing_message = None

# Function to handle user input
def handle_user_message(user_input: str):
    # Add user message to chat history immediately
    timestamp = datetime.now().strftime("%I:%M %p")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Set the message for processing in the next rerun
    st.session_state.processing_message = user_input

# Function to invoke the agent graph to interact with the Travel Planning Agent
async def invoke_agent_graph(user_input: str):
    """
    Run the agent with streaming text for the user_input prompt,
    while maintaining the entire conversation in `st.session_state.messages`.
    """
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # First message from user
    if len(st.session_state.chat_history) == 1:
        user_context = st.session_state.user_context
        initial_state = {
            "user_input": user_input,
            "preferred_airlines": user_context.preferred_airlines,
            "hotel_amenities": user_context.hotel_amenities,
            "budget_level": user_context.budget_level
        }
        async for msg in travel_agent_graph.astream(
                initial_state, config, stream_mode="custom"
            ):
                yield msg
    # Continue the conversation
    else:
        async for msg in travel_agent_graph.astream(
            Command(resume=user_input), config, stream_mode="custom"
        ):
            yield msg

async def main():
    # Sidebar for user preferences
    with st.sidebar:
        st.title("Travel Preferences")
        
        st.subheader("About You")
        traveler_name = st.text_input("Your Name", value="Traveler")
        
        st.subheader("Travel Preferences")
        preferred_airlines = st.multiselect(
            "Preferred Airlines",
            ["SkyWays", "OceanAir", "MountainJet", "Delta", "United", "American", "Southwest"],
            default=st.session_state.user_context.preferred_airlines
        )
        
        preferred_amenities = st.multiselect(
            "Must-have Hotel Amenities",
            ["WiFi", "Pool", "Gym", "Free Breakfast", "Restaurant", "Spa", "Parking"],
            default=st.session_state.user_context.hotel_amenities
        )
        
        budget_level = st.select_slider(
            "Budget Level",
            options=["budget", "mid-range", "luxury"],
            value=st.session_state.user_context.budget_level or "mid-range"
        )
        
        if st.button("Save Preferences"):
            st.session_state.user_context.preferred_airlines = preferred_airlines
            st.session_state.user_context.hotel_amenities = preferred_amenities
            st.session_state.user_context.budget_level = budget_level
            st.success("Preferences saved!")
        
        st.divider()
        
        if st.button("Start New Conversation"):
            st.session_state.chat_history = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.success("New conversation started!")

    # Main chat interface
    st.title("✈️ Travel Planner Assistant")
    st.caption("Give me the details for your trip and let me plan it for you!")

    # Display chat messages
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={st.session_state.user_context.user_id}"):
                st.markdown(message["content"])
                st.caption(message["timestamp"])
        else:
            with st.chat_message("assistant", avatar="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent"):
                st.markdown(message["content"])
                st.caption(message["timestamp"])

    # User input
    # Example: I want to go to Tokyo from Minneapolis. Jun 1st, returning on 6th. Max price for hotel is $300 per night
    user_input = st.chat_input("Let's plan a trip...")
    if user_input:
        handle_user_message(user_input)
        st.rerun()

    # Process message if needed
    if st.session_state.processing_message:
        user_input = st.session_state.processing_message
        st.session_state.processing_message = None
        
        # Process the message asynchronously
        with st.spinner("Thinking..."):
            try:
                # Prepare input for the agent using chat history
                if len(st.session_state.chat_history) > 1:
                    # Convert chat history to input list format for the agent
                    input_list = []
                    for msg in st.session_state.chat_history:
                        input_list.append({"role": msg["role"], "content": msg["content"]})
                else:
                    # First message
                    input_list = user_input

                # Display assistant response in chat message container
                response_content = ""
                
                # Create a chat message container using Streamlit's built-in component
                with st.chat_message("assistant", avatar="https://api.dicebear.com/7.x/bottts/svg?seed=travel-agent"):
                    message_placeholder = st.empty()
                    
                    # Run the async generator to fetch responses
                    async for chunk in invoke_agent_graph(user_input):
                        response_content += chunk
                        # Update only the text content
                        message_placeholder.markdown(response_content)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response_content,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
                
            except Exception as e:
                raise Exception(e)
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
            
            # Force a rerun to display the AI response
            # st.rerun()

    # Footer
    st.divider()
    st.caption("Powered by Pydantic AI and LangGraph | Built with Streamlit")

if __name__ == "__main__":
    asyncio.run(main())