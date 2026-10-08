from langchain_core.tools import tool
import requests  # to make HTTP requests
from bs4 import BeautifulSoup  # library for parsing HTML and XML documents
import os
from rich import print
from config import load_app_secrets

load_app_secrets()

# A global variable to store our RAG database in memory
global_vector_store = None

def get_embeddings():
    load_app_secrets()
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip() != "":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=gemini_key)
        
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key and mistral_key.strip() != "":
        from langchain_mistralai import MistralAIEmbeddings
        return MistralAIEmbeddings(model="mistral-embed", mistral_api_key=mistral_key)

    # Free CPU embeddings for Groq / general use (no API key needed!)
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    except Exception:
        raise ValueError("GROQ_API_KEY or GEMINI_API_KEY is missing in Streamlit Cloud Secrets. Please check your Settings -> Secrets.")





from pydantic import BaseModel, Field

class WebSearchInput(BaseModel):
    query: str = Field(description="The search query keywords to look up on the web.")

class ScrapeUrlInput(BaseModel):
    url: str = Field(description="The exact HTTP or HTTPS URL of the webpage to scrape.")

class RetrieveKnowledgeInput(BaseModel):
    query: str = Field(description="The search query string to look up in the vector database.")

# Create tools with explicit schemas
@tool(args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """Search web for recent and reliable information on topic, return titles, urls, and snippets."""
    load_app_secrets()
    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        return "Error: TAVILY_API_KEY is missing. Please set TAVILY_API_KEY in environment or Streamlit secrets."
    
    try:
        from tavily import TavilyClient
        tavily = TavilyClient(api_key=tavily_key)
        results = tavily.search(query=query, max_results=5)

        out = []
        for r in results.get('results', []):
            title = r.get('title', 'No title')
            url = r.get('url', '')
            content = r.get('content', '')[:300]
            out.append(f"Title: {title}\nURL: {url}\nSnippet: {content}\n")

        if not out:
            return "No web search results found."

        return "\n------\n".join(out)
    except Exception as e:
        return f"Error executing web search: {str(e)}"

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

@tool(args_schema=ScrapeUrlInput)
def scrape_and_store_url(url: str) -> str:
    """Scrape a URL, chunk its content, and store it in the RAG Vector Database."""
    global global_vector_store
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        
        full_text = soup.get_text(separator=" ", strip=True)
        if not full_text or len(full_text) < 50:
            return f"Could not extract meaningful text from URL: {url}"
        
        # 1. Chunking
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        chunks = text_splitter.split_text(full_text)
        
        # 2. Embedding & Vector Store (FAISS)
        embeddings = get_embeddings()
        if global_vector_store is None:
            global_vector_store = FAISS.from_texts(chunks, embeddings)
        else:
            global_vector_store.add_texts(chunks)
            
        return f"Successfully scraped and saved {len(chunks)} text chunks from {url} into our RAG database."
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

@tool(args_schema=RetrieveKnowledgeInput)
def retrieve_knowledge(query: str) -> str:
    """Search the vector database for information relevant to the query."""
    global global_vector_store
    if global_vector_store is None:
        return "No knowledge base available. Please scrape a URL first."
    
    try:
        docs = global_vector_store.similarity_search(query, k=3)
        results = [doc.page_content for doc in docs]
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"Error retrieving knowledge: {str(e)}"
