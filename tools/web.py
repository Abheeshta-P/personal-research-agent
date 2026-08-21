from langchain_core.tools import tool
import requests

from langgraph.prebuilt import InjectedState
from typing import Annotated
# InjectedState injects the graph state into the tool argument automatically.

@tool
def search_web(topic: str, state: Annotated[dict, InjectedState]) -> str:
    """Search the web for a topic."""

    searches_done = state.get("searches_done",[])

    if topic.lower() in searches_done:
        return f"Already searched this query: {topic}. Use the existing evidence."

    print(f"Searching web for: {topic}")

    url = "https://www.google.com/search"

    response = requests.get(
        url,
        params={"q":topic},
        headers={"User-Agent":"Mozilla/5.0"},
        timeout=10
    )

    return response.text[:5000]