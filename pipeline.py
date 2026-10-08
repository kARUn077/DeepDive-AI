from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
from agents import build_reader_agent, build_search_agent, build_writer_agent, get_critic_chain

class GraphState(TypedDict):
    topic: str
    search_results: str
    scraped_content: str
    report: str
    critic_score: int
    feedback: str
    rewrite_count: int

def node_search(state: GraphState):
    print("\n--- [NODE] Search Agent ---")
    topic = state["topic"]
    search_agent = build_search_agent()
    result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    return {"search_results": result['messages'][-1].content, "rewrite_count": 0}

def node_scrape(state: GraphState):
    print("\n--- [NODE] Reader Agent (RAG) ---")
    search_results = state.get("search_results", "")
    topic = state["topic"]
    reader_agent = build_reader_agent()
    result = reader_agent.invoke({
        "messages": [("user",
            f"Based on these search results about '{topic}', use your tool to scrape and store the most relevant URLs into the RAG database.\n\n"
            f"Search Results:\n{search_results[:800]}"
        )]
    })
    return {"scraped_content": result['messages'][-1].content}

def node_write(state: GraphState):
    print("\n--- [NODE] Writer Agent ---")
    topic = state["topic"]
    feedback = state.get("feedback", "")
    rewrite_count = state.get("rewrite_count", 0)
    
    prompt_msg = (
        f"Write a detailed research report on: {topic}.\n"
        f"Structure it clearly with Introduction, Key Findings, and Conclusion.\n"
        f"IMPORTANT: You MUST use your retrieve_knowledge tool to search the database for factual information to include in the report."
    )
    
    # If this is a rewrite loop, we give the Writer the Critic's harsh feedback!
    if feedback and rewrite_count > 0:
        prompt_msg += f"\n\nWARNING - PREVIOUS DRAFT REJECTED!\nThe Critic gave this feedback. You MUST improve the report based on this:\n{feedback}"
    
    writer_agent = build_writer_agent()
    result = writer_agent.invoke({
         "messages": [("user", prompt_msg)]
    })
    
    return {"report": result['messages'][-1].content}

def node_critic(state: GraphState):
    print("\n--- [NODE] Critic Agent ---")
    report = state.get("report", "")
    rewrite_count = state.get("rewrite_count", 0)
    
    critic_chain = get_critic_chain()
    feedback_json = critic_chain.invoke({
        "report": report
    })
    
    score = feedback_json.get("score", 0)
    feedback_text = feedback_json.get("feedback", "")
    
    print(f"Critic Score: {score}/10")
    print(f"Feedback: {feedback_text}")
    
    return {"critic_score": score, "feedback": feedback_text, "rewrite_count": rewrite_count + 1}


def route_after_critic(state: GraphState):
    score = state.get("critic_score", 0)
    rewrite_count = state.get("rewrite_count", 0)
    
    # Pass on score >= 6 or after 1 rewrite to minimize site load & API calls
    if score >= 6 or rewrite_count >= 1:
        print("--> Traffic Light: Score acceptable (>=6) or max rewrite reached. Finishing flow.")
        return "end"
    else:
        print("--> Traffic Light: Score low (<6). Routing back to Writer for 1 quick rewrite.")
        return "rewrite"


# --- Build the Graph ---
workflow = StateGraph(GraphState)

workflow.add_node("Search", node_search)
workflow.add_node("Scrape", node_scrape)
workflow.add_node("Write", node_write)
workflow.add_node("Critic", node_critic)

workflow.set_entry_point("Search")
workflow.add_edge("Search", "Scrape")
workflow.add_edge("Scrape", "Write")
workflow.add_edge("Write", "Critic")

# Conditional Edge
workflow.add_conditional_edges(
    "Critic",
    route_after_critic,
    {
        "end": END,
        "rewrite": "Write"
    }
)

app_graph = workflow.compile()

def run_research_pipeline(topic: str):
    print(f"\nStarting LangGraph pipeline for topic: {topic}")
    
    # This runs the whole flowchart automatically!
    final_state = app_graph.invoke({"topic": topic})
    
    return final_state

if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)
