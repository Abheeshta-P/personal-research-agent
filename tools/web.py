from langchain_core.tools import tool

from langgraph.prebuilt import InjectedState
from typing import Annotated
# InjectedState injects the graph state into the tool argument automatically.

from tavily import TavilyClient
import os


@tool
def search_web(topic: str, state: Annotated[dict, InjectedState]) -> str:
    """Search the web for a topic."""

    # Prevent duplicate web searches for the same topic
    searches_done = state.get("searches_done", [])
    if topic.lower() in searches_done:
        return f"Already searched this query: {topic}. Use the existing evidence."

    print(f"Searching the web for: '{topic}'...")

    # Validate API key availability upfront before attempting search
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "NO_RESULTS: Web search failed: Missing TAVILY_API_KEY in environment variables."

    import time
    response = None
    last_error = None

    # Retry loop: allow up to 2 attempts with a 1s pause between attempts
    for attempt in range(2):
        try:
            client = TavilyClient(api_key=api_key)
            response = client.search(
                query=topic,
                max_results=5,
                search_depth="basic",
            )
            break
        except Exception as e:
            error_msg = str(e)
            # Differentiate quota/rate-limits from timeouts and transient failures
            if "quota" in error_msg.lower() or "rate" in error_msg.lower() or "429" in error_msg:
                return "NO_RESULTS: Web search failed: Tavily API rate limit or quota exceeded."
            if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
                last_error = f"NO_RESULTS: Web search timed out for: {topic}"
            else:
                last_error = f"NO_RESULTS: Web search failed: {e}"

            if attempt == 0:
                time.sleep(1)
                continue

    # Return failure message if all attempts fail
    if response is None:
        return last_error or f"NO_RESULTS: Web search failed for: {topic}"

    results = []
    for result in response.get("results", []):
        results.append(
            f"SOURCE:\n"
            f"Title: {result['title']}\n"
            f"URL: {result['url']}\n\n"
            f"CONTENT:\n{result['content']}"
        )

    # Return standard NO_RESULTS prefix if nothing was found
    if not results:
        return f"NO_RESULTS: No web results found for: {topic}"

    return "\n\n".join(results)