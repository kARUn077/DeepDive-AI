from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from tools import web_search, scrape_and_store_url, retrieve_knowledge
from config import load_app_secrets

load_app_secrets()

# Model setup 
llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

# 1st agent: Search Agent
def build_search_agent():
    # We use LangGraph's built-in agent creator
    return create_react_agent(
        model=llm,
        tools=[web_search]
    )

# 2nd agent: Reader/Scraper Agent
def build_reader_agent():
    return create_react_agent(
        model=llm,
        tools=[scrape_and_store_url]
    )

# 3rd agent: Writer Agent (now uses RAG!)
def build_writer_agent():
    return create_react_agent(
        model=llm,
        tools=[retrieve_knowledge]
    )

# 4th agent: Critic Chain (now structured JSON)
class CriticScore(BaseModel):
    score: int = Field(description="A score out of 10 for the report.")
    feedback: str = Field(description="Constructive feedback, strengths, and areas to improve.")

json_parser = JsonOutputParser(pydantic_object=CriticScore)

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Review the report strictly.\n{format_instructions}"),
    ("human", "Review the research report below:\n\nReport:\n{report}")
]).partial(format_instructions=json_parser.get_format_instructions())

# The critic_chain now automatically parses the output into a Python Dictionary
critic_chain = critic_prompt | llm | json_parser