from langgraph.graph import END, START, StateGraph
from models import InterviewState
from nodes.interview_nodes import (
    generate_question, search_web, search_wikipedia, 
    generate_answer, save_interview, route_messages
)
from nodes.report_nodes import write_section

def build_interview_graph():
    """ Build the interview subgraph """
    interview_builder = StateGraph(InterviewState)
    
    # Add nodes
    interview_builder.add_node("ask_question", generate_question)
    interview_builder.add_node("search_web", search_web)
    interview_builder.add_node("search_wikipedia", search_wikipedia)
    interview_builder.add_node("answer_question", generate_answer)
    interview_builder.add_node("save_interview", save_interview)
    interview_builder.add_node("write_section", write_section)

    # Add edges
    interview_builder.add_edge(START, "ask_question")
    interview_builder.add_edge("ask_question", "search_web")
    interview_builder.add_edge("ask_question", "search_wikipedia")
    interview_builder.add_edge("search_web", "answer_question")
    interview_builder.add_edge("search_wikipedia", "answer_question")
    interview_builder.add_conditional_edges("answer_question", route_messages, ['ask_question', 'save_interview'])
    interview_builder.add_edge("save_interview", "write_section")
    interview_builder.add_edge("write_section", END)
    
    return interview_builder.compile()