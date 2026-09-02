from langchain_core.tools import tool

# source
from config import choose_source

from langchain_core.messages import HumanMessage
from graphs.research_graph import research_graph

@tool
def research(topic: str) -> str:
    """Research a topic using a user-selected source."""
    # select source when research tool call is done
    
    # Prompt user to select their desired research source (Wikipedia, Web, ArXiv, Files, All)
    source = choose_source()

    # Invoke the specialized research subgraph with initialized state
    result = research_graph.invoke({ 
        "messages": [
            HumanMessage(content=f"Research {topic}")
        ], 
        "searches_done": [],
        "sources_used": [],
        "source": source,
        "evidence_found": False,
    })

    # If no evidence was retrieved from the selected source, return structured failure code
    if not result.get("evidence_found", False):
        return f"RESEARCH_FAILED: Could not find relevant information in the selected source: {source}"

    # Safely extract the synthesized answer
    last_msg = result["messages"][-1]
    return getattr(last_msg, "text", None) or getattr(last_msg, "content", str(last_msg))

