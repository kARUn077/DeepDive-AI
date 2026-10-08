import os
from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from tools import web_search, scrape_and_store_url, retrieve_knowledge
from config import load_app_secrets

load_app_secrets()

def get_llm():
    load_app_secrets()
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip() != "":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=gemini_key
        )
    
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key and mistral_key.strip() != "":
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(
            model="mistral-small-latest",
            temperature=0,
            mistral_api_key=mistral_key
        )
    
    raise ValueError("GEMINI_API_KEY is missing. Please set GEMINI_API_KEY in your .env or Streamlit Secrets.")


# 1st agent: Search Agent
def build_search_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[web_search]
    )

# 2nd agent: Reader/Scraper Agent
def build_reader_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[scrape_and_store_url]
    )

# 3rd agent: Writer Agent (uses RAG!)
def build_writer_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[retrieve_knowledge]
    )

# 4th agent: Critic Chain (structured JSON)
class CriticScore(BaseModel):
    score: int = Field(description="A score out of 10 for the report.")
    feedback: str = Field(description="Constructive feedback, strengths, and areas to improve.")

json_parser = JsonOutputParser(pydantic_object=CriticScore)

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Review the report strictly.\n{format_instructions}"),
    ("human", "Review the research report below:\n\nReport:\n{report}")
]).partial(format_instructions=json_parser.get_format_instructions())

def get_critic_chain():
    return critic_prompt | get_llm() | json_parser