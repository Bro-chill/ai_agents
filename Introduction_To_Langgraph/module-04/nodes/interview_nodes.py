from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, get_buffer_string
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools.tavily_search import TavilySearchResults
from config import llm
from models import InterviewState, SearchQuery

question_instructions = """
You are an analyst tasked with interviewing an expert to learn about a specific topic. 

Your goal is boil down to interesting and specific insights related to your topic.

1. Interesting: Insights that people will find surprising or non-obvious.        
2. Specific: Insights that avoid generalities and include specific examples from the expert.

Here is your topic of focus and set of goals: {goals}
Begin by introducing yourself using a name that fits your persona, and then ask your question.
Continue to ask questions to drill down and refine your understanding of the topic.
When you are satisfied with your understanding, complete the interview with: "Thank you so much for your help!"
Remember to stay in character throughout your response, reflecting the persona and goals provided to you.
"""

search_instructions = SystemMessage(
    content=f"""You will be given a conversation between an analyst and an expert. 

    Your goal is to generate a well-structured query for use in retrieval and / or web-search related to the conversation.
    First, analyze the full conversation.
    Pay particular attention to the final question posed by the analyst.
    Convert this final question into a well-structured web search query"""
)

answer_instructions = """
You are an expert being interviewed by an analyst.
Here is analyst area of focus: {goals}. 
You goal is to answer a question posed by the interviewer.
To answer question, use this context: {context}

When answering questions, follow these guidelines:
1. Use only the information provided in the context. 
2. Do not introduce external information or make assumptions beyond what is explicitly stated in the context.
3. The context contain sources at the topic of each individual document.
4. Include these sources your answer next to any relevant statements. For example, for source # 1 use [1]. 
5. List your sources in order at the bottom of your answer. [1] Source 1, [2] Source 2, etc
6. If the source is: <Document source="assistant/docs/llama3_1.pdf" page="7"/>' then just list: 
        
[1] assistant/docs/llama3_1.pdf, page 7 
        
And skip the addition of the brackets as well as the Document source preamble in your citation.
"""

def generate_question(state: InterviewState):
    """ Node to generate a question """
    analyst = state["analyst"]
    messages = state["messages"]

    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)
        
    return {"messages": [question]}

def search_web(state: InterviewState):
    """ Retrieve docs from web search """
    tavily_search = TavilySearchResults(max_results=3)

    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions] + state['messages'])
    
    search_docs = tavily_search.invoke(search_query.search_query)

    formatted_search_docs = "\n\n---\n\n".join([
        f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
        for doc in search_docs
    ])

    return {"context": [formatted_search_docs]} 

def search_wikipedia(state: InterviewState):
    """ Retrieve docs from wikipedia """
    structured_llm = llm.with_structured_output(SearchQuery)
    search_query = structured_llm.invoke([search_instructions] + state['messages'])
    
    search_docs = WikipediaLoader(
        query=search_query.search_query,
        load_max_docs=2
    ).load()

    formatted_search_docs = "\n\n---\n\n".join([
        f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
        for doc in search_docs
    ])

    return {"context": [formatted_search_docs]} 

def generate_answer(state: InterviewState):    
    """ Node to answer a question """
    analyst = state["analyst"]
    messages = state["messages"]
    context = state["context"]

    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer = llm.invoke([SystemMessage(content=system_message)] + messages)
            
    answer.name = "expert"
    
    return {"messages": [answer]}

def save_interview(state: InterviewState):
    """ Save interviews """
    messages = state["messages"]
    interview = get_buffer_string(messages)
    return {"interview": interview}

def route_messages(state: InterviewState, name: str = "expert"):
    """ Route between question and answer """
    messages = state["messages"]
    max_num_turns = state.get('max_num_turns', 2)

    num_responses = len([m for m in messages if isinstance(m, AIMessage) and m.name == name])

    if num_responses >= max_num_turns:
        return 'save_interview'

    last_question = messages[-2]
    
    if "Thank you so much for your help" in last_question.content:
        return 'save_interview'
    return "ask_question"