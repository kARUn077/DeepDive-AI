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

from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Initialize Mistral Embeddings
embeddings = MistralAIEmbeddings(model="mistral-embed")

# A global variable to store our RAG database in memory
global_vector_store = None

@tool
def scrape_and_store_url(url: str) -> str:
    """Scrape a URL, chunk its content, and store it in the RAG Vector Database."""
    global global_vector_store
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        
        # Get the full text instead of just 3000 chars
        full_text = soup.get_text(separator=" ", strip=True)
        
        # 1. Chunking: split the big text into smaller ~1000 character pieces
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100
        )
        chunks = text_splitter.split_text(full_text)
        
        # 2. Embedding & Vector Store (FAISS)
        if global_vector_store is None:
            # Create the database for the first time
            global_vector_store = FAISS.from_texts(chunks, embeddings)
        else:
            # Add to the existing database
            global_vector_store.add_texts(chunks)
            
        return f"Successfully scraped and saved {len(chunks)} text chunks from {url} into our RAG database."
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

@tool
def retrieve_knowledge(query: str) -> str:
    """Search the vector database for information relevant to the query."""
    global global_vector_store
    if global_vector_store is None:
        return "No knowledge base available. Please scrape a URL first."
    
    # Search the database for the top 3 most relevant chunks to the query
    docs = global_vector_store.similarity_search(query, k=3)
    results = [doc.page_content for doc in docs]
    
    # Return them separated by lines
    return "\n\n---\n\n".join(results)