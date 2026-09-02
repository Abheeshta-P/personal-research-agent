from langchain_core.tools import tool

from langgraph.prebuilt import InjectedState
from typing import Annotated
# InjectedState injects the graph state into the tool argument automatically.

from tavily import TavilyClient
import os


@tool
def search_web(topic: str, state: Annotated[dict, InjectedState]) -> str:
    """Search the web for a topic."""

    searches_done = state.get("searches_done", [])

    if topic.lower() in searches_done:
        return f"Already searched this query: {topic}. Use the existing evidence."

    print(f"Searching web for: {topic}")

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=topic,
        max_results=5,
        search_depth="basic",
    )

    results = []

    for result in response["results"]:
        results.append(
            f"SOURCE:\n"
            f"Title: {result['title']}\n"
            f"URL: {result['url']}\n\n"
            f"CONTENT:\n{result['content']}"
        )

    if not results:
        return f"NO_RESULTS: No web results found for: {topic}"

    return "\n\n".join(results)