from langchain_core.tools import tool

# source
from config import choose_source

from langchain_core.messages import HumanMessage
from graphs.research_graph import research_graph

# Global override for research source (used by Streamlit UI or programmatic execution)
_active_source = None

def set_active_source(source: str | None):
    """Set default or override research source (useful for UI or non-interactive runs)."""
    global _active_source
    _active_source = source

def get_active_source() -> str | None:
    return _active_source

def normalize_source(name: str) -> str:
    """Normalize user-friendly source names to canonical keys."""
    if not name:
        return "All"
    s = str(name).strip().lower()
    if "wiki" in s:
        return "Wikipedia"
    if "arxiv" in s or "paper" in s:
        return "Research Papers"
    if "file" in s or "doc" in s:
        return "Files"
    if "web" in s or "tavily" in s or "internet" in s:
        return "Web"
    return "All"

@tool
def research(topic: str) -> str:
    """Research a topic using a user-selected source."""

    # Use active source if set (e.g. from Streamlit UI), otherwise prompt user via CLI
    if _active_source:
        chosen_source = normalize_source(_active_source)
    else:
        chosen_source = choose_source()

    # Invoke the specialized research subgraph with initialized state
    result = research_graph.invoke({ 
        "messages": [
            HumanMessage(content=f"Research {topic}")
        ], 
        "searches_done": [],
        "sources_used": [],
        "source": chosen_source,
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
                    return f"RESEARCH_FAILED: Search timed out for source: {chosen_source}. Please try again."
                elif "quota" in lower_c or "rate limit" in lower_c or "429" in lower_c:
                    return f"RESEARCH_FAILED: Rate limit reached for source: {chosen_source}. Please wait a moment and try again."
                elif "missing tavily_api_key" in lower_c or "api key" in lower_c:
                    return f"RESEARCH_FAILED: API key error for source {chosen_source}. Please check your environment variables."
                elif "search failed" in lower_c:
                    return f"RESEARCH_FAILED: Connection to source {chosen_source} failed: {content_str.replace('NO_RESULTS:', '').strip()}"
                break
        return f"RESEARCH_FAILED: Could not find relevant information in the selected source: {chosen_source}"

    # Safely extract the synthesized answer
    last_msg = result["messages"][-1]
    answer_text = getattr(last_msg, "text", None) or getattr(last_msg, "content", str(last_msg))

    if isinstance(answer_text, list):
        parts = []
        for part in answer_text:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
        answer_text = "\n".join(parts)

    # Catch cases where the researcher LLM judged retrieved documents as irrelevant and stated no info found
    if isinstance(answer_text, str) and "could not find relevant information in the selected source" in answer_text.lower():
        return f"RESEARCH_FAILED: Could not find relevant information in the selected source: {chosen_source}"

    return answer_text
