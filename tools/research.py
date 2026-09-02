from langchain_core.tools import tool

# source
from config import choose_source

from langchain_core.messages import HumanMessage
from graphs.research_graph import research_graph

@tool
def research(topic: str) -> str:
    """Research a topic using a user-selected source."""
    # select source when research tool call is done

    source = choose_source()

    # call the llm with research tool as first step 
    result = research_graph.invoke({ 
        "messages": [
            HumanMessage(content=f"Research {topic}")
        ], 
        "searches_done": [],
        "sources_used": [],
        "source": source,
        "evidence_found": False,
    })

    print("\n[DEBUG] research() FINAL RESULT:")
    print("evidence_found:", result.get("evidence_found"))
    print("last_message:", result["messages"][-1])

    if not result.get("evidence_found", False):
     return f"RESEARCH_FAILED: Could not find relevant information in the selected source: {source}"

    return result["messages"][-1].text

