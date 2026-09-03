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

    # If no evidence was retrieved from the selected source, check for timeout, rate limit, or connection errors
    if not result.get("evidence_found", False):
        for msg in reversed(result.get("messages", [])):
            if msg.type == "tool":
                content_str = str(msg.content)
                lower_c = content_str.lower()
                # Surface specific infrastructure errors to the user rather than claiming no information exists
                if "timed out" in lower_c:
                    return f"RESEARCH_FAILED: Search timed out for source: {source}. Please try again."
                elif "quota" in lower_c or "rate limit" in lower_c or "429" in lower_c:
                    return f"RESEARCH_FAILED: Rate limit reached for source: {source}. Please wait a moment and try again."
                elif "missing tavily_api_key" in lower_c or "api key" in lower_c:
                    return f"RESEARCH_FAILED: API key error for source {source}. Please check your environment variables."
                elif "search failed" in lower_c:
                    return f"RESEARCH_FAILED: Connection to source {source} failed: {content_str.replace('NO_RESULTS:', '').strip()}"
                break
        return f"RESEARCH_FAILED: Could not find relevant information in the selected source: {source}"

    # Safely extract the synthesized answer
    last_msg = result["messages"][-1]
    answer_text = getattr(last_msg, "text", None) or getattr(last_msg, "content", str(last_msg))

    # Catch cases where the researcher LLM judged retrieved documents as irrelevant and stated no info found
    if isinstance(answer_text, str) and "could not find relevant information in the selected source" in answer_text.lower():
        return f"RESEARCH_FAILED: Could not find relevant information in the selected source: {source}"

    return answer_text

