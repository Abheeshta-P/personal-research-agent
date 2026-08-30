from langchain_core.tools import tool

# source
from core.config import choose_source

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
    })

    return result["messages"][-1].text

