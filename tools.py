from langchain_core.tools import tool
import requests  #to make HTTP requests
from bs4 import BeautifulSoup #it is a library for parsing HTML and XML documents

from tavily import TavilyClient
import os
from rich import print
from config import load_app_secrets

load_app_secrets()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

#create tool
@tool
def web_search(query: str) -> str:
    """
    Search web for recent and reliable information on topic , return titles and urls and snippets.
    """

    results = tavily.search(query=query, max_results=5)  # Search the web for the query and return top 5 results

    out = []
    for r in results['results']:
        out.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n")

    return "\n------\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"