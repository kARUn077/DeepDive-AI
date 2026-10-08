import os
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from tools import web_search, scrape_and_store_url, retrieve_knowledge
from config import load_app_secrets

load_app_secrets()


def get_llm():
    load_app_secrets()

    # 1. Try Groq API (Primary Choice - Llama 3.3 70B, Blazing Fast)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key.strip() != "":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            groq_api_key=groq_key
        )



    # 2. Try Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip() != "":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0,
            google_api_key=gemini_key,
            max_retries=3
        )

    # 3. Try Mistral API
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key and mistral_key.strip() != "":
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(
            model="mistral-small-latest",
            temperature=0,
            mistral_api_key=mistral_key
        )

    raise ValueError(
        "GROQ_API_KEY or GEMINI_API_KEY is missing in Streamlit Cloud Secrets. "
        "Please add GROQ_API_KEY under Settings -> Secrets."
    )



# 1st Agent: Search Agent
def build_search_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[web_search]
    )


# 2nd Agent: Reader/Scraper Agent
def build_reader_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[scrape_and_store_url]
    )


# 3rd Agent: Writer Agent
def build_writer_agent():
    return create_react_agent(
        model=get_llm(),
        tools=[retrieve_knowledge]
    )


# 4th Agent: Critic Chain
class CriticScore(BaseModel):
    score: int = Field(
        description="A score out of 10 for the report."
    )
    feedback: str = Field(
        description="Constructive feedback, strengths, and areas to improve."
    )


json_parser = JsonOutputParser(
    pydantic_object=CriticScore
)


critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. "
        "Review the report strictly.\n{format_instructions}"
    ),
    (
        "human",
        "Review the research report below:\n\nReport:\n{report}"
    )
]).partial(
    format_instructions=json_parser.get_format_instructions()
)


def get_critic_chain():
    return critic_prompt | get_llm() | json_parser