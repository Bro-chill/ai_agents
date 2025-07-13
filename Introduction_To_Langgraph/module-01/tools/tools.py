import requests

from langchain.agents import tool
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults

from config.settings import TAVILY_API_KEY

@tool
def calculator(expression: str) -> str:
    """Performs mathematical calculations."""
    try:
        expression = expression.replace('^','**')
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
    
@tool
def wikipedia_search(query: str) -> str:
    """Search Wikipedia for information about a topic"""
    try:
        wikipedia = WikipediaAPIWrapper()
        result = wikipedia.run(query)
        return result
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

@tool
def research_paper_search(query: str) -> str:
    """Search Research Paper about a topic"""
    try:
        arxiv = ArxivAPIWrapper()
        result = arxiv.run(query)
        return result
    except Exception as e:
        return f"Error searching For Research Paper: {str(e)}"

@tool
def tavily_search(query: str) -> str:
    """Search using Tavily information about a topic"""
    try:
        tavily_search = TavilySearchResults(
            max_results=3,
            tavily_api_key=TAVILY_API_KEY
        )
        result = tavily_search.invoke(query)
        return result
    except Exception as e:
        return f"Error searching using Tavily: {str(e)}"
    
@tool
def currency_exchange(base: str, symbol: str) -> str:
    """Search Latest Currency Rate"""
    try:
        base_url = "https://api.frankfurter.dev/v1/latest"
        url = f"{base_url}?base={base}&symbols={symbol}"
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        return f"Error to convert currency: {str(e)}"