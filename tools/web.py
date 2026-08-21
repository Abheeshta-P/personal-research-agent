from langchain_core.tools import tool
import requests

from langgraph.prebuilt import ToolNode, InjectedState
from typing import Annotated

@tool
def search_web(topic: str, searches_done: list[str]) -> str:
    """Search the web for a topic."""

    if topic.lower() in searches_done:
        return f"Already searched for: {topic}. Use the existing evidence."

    print(f"Searching web for: {topic}")

    url = "https://www.google.com/search"

    response = requests.get(
        url,
        params={"q":topic},
        headers={"User-Agent":"Mozilla/5.0"},
        timeout=10
    )

    return f"Searched: {topic}\n\n{response}"