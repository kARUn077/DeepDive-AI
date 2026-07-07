from langchain_core.tools import tool
import requests  #to make HTTP requests
from bs4 import BeautifulSoup #it is a library for parsing HTML and XML documents

from tavily import TavilyClient
import os
from rich import print
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#create tool
@tool
def websearch(query: str) -> str:
    """
    Search web for recent and reliable information on topic , return titles and urls and snippets.
    """

    results = tavily.search(query=query, max_results=5)  # Search the web for the query and return top 5 results

    out = []
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")

    return "\n------\n".join(out)

print(websearch.invoke("What is the latest news on war?"))  # Example usage of the websearch tool